from collections.abc import AsyncIterator

from openai import AsyncOpenAI

from app.ai.llm.base_llm import BaseLLM
from app.core.config import settings


class OpenAIProvider(BaseLLM):
    """LLM provider backed by OpenAI's API (paid — used only if explicitly configured)."""

    def __init__(self) -> None:
        self._client = AsyncOpenAI(api_key=settings.openai_api_key)

    async def generate(self, prompt: str, system_prompt: str | None = None) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = await self._client.chat.completions.create(
            model=settings.openai_model,
            messages=messages,
        )
        return response.choices[0].message.content or ""

    async def generate_stream(self, prompt: str, system_prompt: str | None = None) -> AsyncIterator[str]:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        stream = await self._client.chat.completions.create(
            model=settings.openai_model,
            messages=messages,
            stream=True,
        )
        async for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta