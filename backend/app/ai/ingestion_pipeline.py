import uuid

from app.ai.embeddings import get_embedder
from app.ai.vectorstore.chroma_client import get_or_create_collection, get_organization_collection_name
from app.core.logging import get_logger
from app.processing.chunking import chunk_text

logger = get_logger(__name__)


def ingest_document_text(
    organization_id: uuid.UUID,
    document_id: uuid.UUID,
    document_title: str,
    file_type: str,
    extracted_text: str,
) -> int:
    """Chunk, embed, and store a document's extracted text in the vector store.

    Returns the number of chunks successfully ingested. Existing chunks for
    this document (from a prior version) are cleared first, so re-ingestion
    is idempotent.
    """
    collection_name = get_organization_collection_name(str(organization_id))
    collection = get_or_create_collection(collection_name)

    # Remove any previously ingested chunks for this document (e.g. from an
    # earlier version), so re-processing doesn't leave stale duplicates.
    collection.delete(where={"document_id": str(document_id)})

    chunks = chunk_text(extracted_text, chunk_size=1000, chunk_overlap=150)
    if not chunks:
        logger.warning("No chunks produced for document %s — text may be empty", document_id)
        return 0

    embedder = get_embedder()
    chunk_contents = [chunk.content for chunk in chunks]
    embeddings = embedder.embed_batch(chunk_contents)

    ids = [f"{document_id}_{chunk.chunk_index}" for chunk in chunks]
    metadatas = [
        {
            "document_id": str(document_id),
            "organization_id": str(organization_id),
            "document_title": document_title,
            "file_type": file_type,
            "chunk_index": chunk.chunk_index,
            "start_char": chunk.start_char,
            "end_char": chunk.end_char,
        }
        for chunk in chunks
    ]

    collection.add(
        ids=ids,
        embeddings=embeddings,
        documents=chunk_contents,
        metadatas=metadatas,
    )

    logger.info("Ingested %d chunks for document %s", len(chunks), document_id)
    return len(chunks)