import logging
import asyncio

from openai import AsyncOpenAI

from src.core.config import Settings

logger = logging.getLogger(__name__)


class SummarizationService:
    def __init__(self, openai_client: AsyncOpenAI, settings: Settings):
        self.client = openai_client
        self.settings = settings

        self.model = settings.LLM_MODEL_NAME
        self.temperature = settings.LLM_TEMPERATURE

        self.max_retries = 2
        self.timeout = 30

    async def _call_llm_with_retry(self, prompt: str) -> str:
        for attempt in range(self.max_retries + 1):
            try:
                response = await asyncio.wait_for(
                    self.client.chat.completions.create(
                        model=self.model,
                        messages=[{"role": "user", "content": prompt}],
                        temperature=self.temperature,
                    ),
                    timeout=self.timeout,
                )

                return response.choices[0].message.content

            except Exception as e:
                logger.warning(f"LLM attempt {attempt + 1} failed: {e}")

                if attempt == self.max_retries:
                    raise

                await asyncio.sleep(1)
