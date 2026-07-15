from app.ai.llm.base_llm import BaseLLM
from app.core.config import settings

_llm_instance: BaseLLM | None = None


def get_llm() -> BaseLLM:
    """Return a singleton LLM provider instance, chosen by config.

    Switching providers is a one-line env var change (LLM_PROVIDER=gemini
    | openai | ollama) — no other code needs to change.
    """
    global _llm_instance
    if _llm_instance is None:
        if settings.llm_provider == "gemini":
            from app.ai.llm.gemini_provider import GeminiProvider
            _llm_instance = GeminiProvider()
        elif settings.llm_provider == "openai":
            from app.ai.llm.openai_provider import OpenAIProvider
            _llm_instance = OpenAIProvider()
        elif settings.llm_provider == "ollama":
            from app.ai.llm.ollama_provider import OllamaProvider
            _llm_instance = OllamaProvider()
        else:
            raise ValueError(f"Unknown LLM provider: {settings.llm_provider}")

    return _llm_instance