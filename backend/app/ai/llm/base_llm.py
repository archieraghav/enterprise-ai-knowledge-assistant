from abc import ABC, abstractmethod
from collections.abc import AsyncIterator


class BaseLLM(ABC):
    """Defines the contract every LLM provider must implement."""

    @abstractmethod
    async def generate(self, prompt: str, system_prompt: str | None = None) -> str:
        """Generate a single text completion for the given prompt."""
        raise NotImplementedError

    @abstractmethod
    async def generate_stream(self, prompt: str, system_prompt: str | None = None) -> AsyncIterator[str]:
        """Generate a text completion, yielding chunks of text as they arrive."""
        raise NotImplementedError
        yield  # pragma: no cover — makes this an async generator for type checkers