from app.ai.embeddings.base_embedder import BaseEmbedder
from app.ai.embeddings.sentence_transformer_embedder import SentenceTransformerEmbedder

_embedder_instance: BaseEmbedder | None = None


def get_embedder() -> BaseEmbedder:
    """Return a singleton embedder instance.

    Swapping providers later (e.g. to OpenAI) means changing only this
    function — nothing else in the codebase references a specific
    embedder class directly.
    """
    global _embedder_instance
    if _embedder_instance is None:
        _embedder_instance = SentenceTransformerEmbedder()
    return _embedder_instance