from collections.abc import AsyncIterator

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

    async def generate_stream(self, prompt: str, system_prompt: str | None = None) -> AsyncIterator[str]:
        full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
        response = await self._model.generate_content_async(full_prompt, stream=True)
        async for chunk in response:
            if chunk.text:
                yield chunk.text