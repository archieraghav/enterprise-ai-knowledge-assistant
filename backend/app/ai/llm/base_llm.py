from abc import ABC, abstractmethod


class BaseLLM(ABC):
    """Defines the contract every LLM provider must implement.

    This abstraction allows swapping between Gemini (free), OpenAI (paid),
    or Ollama (local) without changing any code that consumes LLM responses.
    """

    @abstractmethod
    async def generate(self, prompt: str, system_prompt: str | None = None) -> str:
        """Generate a single text completion for the given prompt."""
        raise NotImplementedError