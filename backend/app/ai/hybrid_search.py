import uuid

from rank_bm25 import BM25Okapi

from app.ai.retriever import RetrievedChunk, retrieve_relevant_chunks
from app.ai.vectorstore.chroma_client import get_or_create_collection, get_organization_collection_name
from app.ai.vectorstore.metadata_filters import MetadataFilter
from app.core.logging import get_logger

logger = get_logger(__name__)


def _tokenize(text: str) -> list[str]:
    """Simple whitespace + lowercase tokenizer for BM25."""
    return text.lower().split()


def _bm25_search(
    organization_id: uuid.UUID, query: str, top_k: int
) -> list[RetrievedChunk]:
    """Run a keyword-based BM25 search over all chunks in an organization's collection.

    Fetches all documents from the collection to build the BM25 index in
    memory — fine for this project's scale, but a production system with
    huge document volumes would maintain a persistent BM25 index instead
    of rebuilding it per query.
    """
    collection_name = get_organization_collection_name(str(organization_id))
    collection = get_or_create_collection(collection_name)

    all_data = collection.get(include=["documents", "metadatas"])
    documents = all_data.get("documents", [])
    metadatas = all_data.get("metadatas", [])

    if not documents:
        return []

    tokenized_corpus = [_tokenize(doc) for doc in documents]
    bm25 = BM25Okapi(tokenized_corpus)

    tokenized_query = _tokenize(query)
    scores = bm25.get_scores(tokenized_query)

    scored_results = sorted(
        zip(documents, metadatas, scores), key=lambda x: x[2], reverse=True
    )[:top_k]

    chunks = []
    for content, metadata, score in scored_results:
        if score <= 0:
            continue
        chunks.append(
            RetrievedChunk(
                content=content,
                document_id=metadata.get("document_id", ""),
                document_title=metadata.get("document_title", "Unknown"),
                chunk_index=metadata.get("chunk_index", 0),
                distance=1.0 / (1.0 + score),  # Convert BM25 score to distance-like scale
            )
        )
    return chunks


def hybrid_search(
    organization_id: uuid.UUID,
    query: str,
    top_k: int = 5,
    metadata_filter: MetadataFilter | None = None,
) -> list[RetrievedChunk]:
    """Combine semantic (vector) and keyword (BM25) search results.

    Uses reciprocal rank fusion: each chunk's final score is based on its
    rank position in each result list, rewarding chunks that appear in both.
    """
    semantic_results = retrieve_relevant_chunks(organization_id, query, top_k=top_k * 2, metadata_filter=metadata_filter)
    keyword_results = _bm25_search(organization_id, query, top_k=top_k * 2)

    rrf_scores: dict[str, float] = {}
    chunk_lookup: dict[str, RetrievedChunk] = {}

    k = 60  # standard RRF constant, dampens the impact of rank position

    for rank, chunk in enumerate(semantic_results):
        key = f"{chunk.document_id}_{chunk.chunk_index}"
        rrf_scores[key] = rrf_scores.get(key, 0) + 1.0 / (k + rank + 1)
        chunk_lookup[key] = chunk

    for rank, chunk in enumerate(keyword_results):
        key = f"{chunk.document_id}_{chunk.chunk_index}"
        rrf_scores[key] = rrf_scores.get(key, 0) + 1.0 / (k + rank + 1)
        chunk_lookup.setdefault(key, chunk)

    ranked_keys = sorted(rrf_scores.keys(), key=lambda k: rrf_scores[k], reverse=True)

    return [chunk_lookup[key] for key in ranked_keys[:top_k]]