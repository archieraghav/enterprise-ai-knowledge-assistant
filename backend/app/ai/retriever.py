import uuid
from dataclasses import dataclass

from app.ai.embeddings import get_embedder
from app.ai.vectorstore.chroma_client import get_organization_collection_name, search_collection
from app.ai.vectorstore.metadata_filters import MetadataFilter
from app.core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class RetrievedChunk:
    """A single chunk of document text retrieved as relevant context for a query."""

    content: str
    document_id: str
    document_title: str
    chunk_index: int
    distance: float


def retrieve_relevant_chunks(
    organization_id: uuid.UUID,
    query: str,
    top_k: int = 5,
    metadata_filter: MetadataFilter | None = None,
) -> list[RetrievedChunk]:
    """Retrieve the most semantically relevant document chunks for a natural-language query.

    Returns an empty list if the organization has no ingested documents yet,
    rather than raising an error — callers should handle "no context found"
    gracefully (e.g. tell the user no documents match).
    """
    embedder = get_embedder()
    query_embedding = embedder.embed_text(query)

    collection_name = get_organization_collection_name(str(organization_id))
    where = metadata_filter.to_chroma_where() if metadata_filter else None

    try:
        results = search_collection(collection_name, query_embedding, top_k=top_k, where=where)
    except Exception:
        logger.exception("Vector search failed for organization %s", organization_id)
        return []

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    chunks = []
    for content, metadata, distance in zip(documents, metadatas, distances):
        chunks.append(
            RetrievedChunk(
                content=content,
                document_id=metadata.get("document_id", ""),
                document_title=metadata.get("document_title", "Unknown"),
                chunk_index=metadata.get("chunk_index", 0),
                distance=distance,
            )
        )

    return chunks