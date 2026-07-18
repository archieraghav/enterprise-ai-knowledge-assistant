import chromadb
from chromadb.api.models.Collection import Collection

from app.core.config import settings

_chroma_client: chromadb.ClientAPI | None = None


def get_chroma_client() -> chromadb.ClientAPI:
    """Return a singleton ChromaDB client.

    Uses Chroma Cloud (CloudClient) when an API key is configured —
    the production path. Falls back to a local HttpClient for Docker
    Compose development when no cloud API key is set.
    """
    global _chroma_client
    if _chroma_client is None:
        if settings.chroma_api_key:
            _chroma_client = chromadb.CloudClient(
                api_key=settings.chroma_api_key,
                tenant=settings.chroma_tenant,
                database=settings.chroma_database,
            )
        else:
            _chroma_client = chromadb.HttpClient(
                host=settings.chroma_host,
                port=settings.chroma_port,
            )
    return _chroma_client


def get_or_create_collection(collection_name: str) -> Collection:
    """Return a ChromaDB collection, creating it if it doesn't already exist."""
    client = get_chroma_client()
    return client.get_or_create_collection(name=collection_name)


def get_organization_collection_name(organization_id: str) -> str:
    """Build a namespaced collection name so each organization's vectors stay isolated."""
    return f"org_{organization_id.replace('-', '_')}"


def search_collection(
    collection_name: str,
    query_embedding: list[float],
    top_k: int = 5,
    where: dict | None = None,
) -> dict:
    """Run a similarity search against a collection, with optional metadata filtering."""
    client = get_chroma_client()
    collection = client.get_or_create_collection(name=collection_name)

    query_kwargs: dict = {
        "query_embeddings": [query_embedding],
        "n_results": top_k,
        "include": ["documents", "metadatas", "distances"],
    }
    if where is not None:
        query_kwargs["where"] = where

    return collection.query(**query_kwargs)