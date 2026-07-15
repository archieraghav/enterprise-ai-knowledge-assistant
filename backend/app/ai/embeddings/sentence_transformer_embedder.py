from sentence_transformers import SentenceTransformer

from app.ai.embeddings.base_embedder import BaseEmbedder

# all-MiniLM-L6-v2: small, fast, free, 384-dimensional — a solid default
# for local embedding generation with no API costs.
_MODEL_NAME = "all-MiniLM-L6-v2"
_EMBEDDING_DIMENSION = 384


class SentenceTransformerEmbedder(BaseEmbedder):
    """Generates embeddings locally using a free sentence-transformers model.

    The model downloads automatically on first use (cached afterward in
    ~/.cache/torch/sentence_transformers/) — no API key or internet
    connection required after that initial download.
    """

    def __init__(self) -> None:
        self._model = SentenceTransformer(_MODEL_NAME)

    def embed_text(self, text: str) -> list[float]:
        embedding = self._model.encode(text, convert_to_numpy=True)
        return embedding.tolist()

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        embeddings = self._model.encode(texts, convert_to_numpy=True, batch_size=32)
        return embeddings.tolist()

    @property
    def dimension(self) -> int:
        return _EMBEDDING_DIMENSION