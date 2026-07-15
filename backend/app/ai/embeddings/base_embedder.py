from abc import ABC, abstractmethod


class BaseEmbedder(ABC):
    """Defines the contract every embedding provider must implement.

    This abstraction allows swapping between free local models
    (sentence-transformers) and paid API-based models (OpenAI) without
    changing any code that consumes embeddings.
    """

    @abstractmethod
    def embed_text(self, text: str) -> list[float]:
        """Generate a single embedding vector for one piece of text."""
        raise NotImplementedError

    @abstractmethod
    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Generate embedding vectors for multiple texts efficiently."""
        raise NotImplementedError

    @property
    @abstractmethod
    def dimension(self) -> int:
        """Return the vector dimension this embedder produces."""
        raise NotImplementedError