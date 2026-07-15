import google.generativeai as genai

from app.ai.llm.base_llm import BaseLLM
from app.core.config import settings


class GeminiProvider(BaseLLM):
    """LLM provider backed by Google's Gemini free-tier API."""

    def __init__(self) -> None:
        genai.configure(api_key=settings.gemini_api_key)
        self._model = genai.GenerativeModel(settings.gemini_model)

    async def generate(self, prompt: str, system_prompt: str | None = None) -> str:
        full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
        response = await self._model.generate_content_async(full_prompt)
        return response.text