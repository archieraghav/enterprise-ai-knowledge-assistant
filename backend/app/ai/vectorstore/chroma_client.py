import chromadb
from chromadb.api.models.Collection import Collection

from app.core.config import settings

_chroma_client: chromadb.ClientAPI | None = None


def get_chroma_client() -> chromadb.ClientAPI:
    """Return a singleton ChromaDB HTTP client, connected to the Docker Compose service."""
    global _chroma_client
    if _chroma_client is None:
        _chroma_client = chromadb.HttpClient(host=settings.chroma_host, port=settings.chroma_port)
    return _chroma_client


def get_or_create_collection(collection_name: str) -> Collection:
    """Return a ChromaDB collection, creating it if it doesn't already exist."""
    client = get_chroma_client()
    return client.get_or_create_collection(name=collection_name)


def get_organization_collection_name(organization_id: str) -> str:
    """Build a namespaced collection name so each organization's vectors stay isolated."""
    return f"org_{organization_id.replace('-', '_')}"