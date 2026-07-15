import httpx

from app.ai.llm.base_llm import BaseLLM
from app.core.config import settings


class OllamaProvider(BaseLLM):
    """LLM provider backed by a locally running Ollama instance (fully free, offline)."""

    async def generate(self, prompt: str, system_prompt: str | None = None) -> str:
        full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt

        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{settings.ollama_base_url}/api/generate",
                json={"model": settings.ollama_model, "prompt": full_prompt, "stream": False},
            )
            response.raise_for_status()
            return response.json()["response"]