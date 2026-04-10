import logging
import json
import asyncio
from typing import List, Optional

from openai import AsyncOpenAI
from pydantic import HttpUrl

from src.core.config import get_settings
from src.ai_engine.data_fetchers.distillation_retrieval import retrieve_chunks_by_url
from src.ai_engine.llm_generators.distillation_prompts import get_distillation_prompt
from src.core.exceptions import DistillationError
from src.models.distillation_schemas import SingleDistilledItem, DistilledContent

logger = logging.getLogger(__name__)


class ContentDistiller:
    def __init__(self):
        settings = get_settings()
        self.client = AsyncOpenAI(
            api_key=settings.GEMINI_API_KEY,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        )
        # Maximum character limit for the LLM prompt to avoid token overflow
        self.MAX_CHARS = 100000

    def _truncate_chunks(self, chunks: List[str]) -> List[str]:
        """
        Truncates the list of text chunks to ensure the total length stays within MAX_CHARS.
        """
        truncated_chunks = []
        current_length = 0

        for chunk in chunks:
            if current_length + len(chunk) > self.MAX_CHARS:
                break
            truncated_chunks.append(chunk)
            current_length += len(chunk)

        return truncated_chunks

    async def _distill_single_url(
        self, url: HttpUrl, is_primary: bool = False
    ) -> SingleDistilledItem:
        """
        Processes a single URL: retrieves chunks, distills content via LLM,
        and marks it as primary if specified.
        """
        try:
            chunks = await retrieve_chunks_by_url(str(url))

            safe_chunks = self._truncate_chunks(chunks)
            prompt = get_distillation_prompt(safe_chunks)

            response = await self.client.chat.completions.create(
                model="gemini-2.0-flash",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that distills content into JSON.",
                    },
                    {"role": "user", "content": prompt},
                ],
                response_format={"type": "json_object"},
            )

            distilled_dict = json.loads(response.choices[0].message.content)

            return SingleDistilledItem(
                url=url,
                distilled_content=DistilledContent(**distilled_dict),
                is_primary=is_primary,
            )

        except Exception as e:
            logger.error(f"Distillation failed for {url}: {str(e)}")
            raise DistillationError(f"Failed to distill {url}: {e}")

    async def distill_multiple_urls(
        self, urls: List[HttpUrl], primary_url: Optional[HttpUrl] = None
    ) -> List[SingleDistilledItem]:
        """
        Orchestrates the distillation of multiple URLs concurrently.
        """
        tasks = []

        for url in urls:
            is_primary = (str(url) == str(primary_url)) if primary_url else False
            tasks.append(self._distill_single_url(url, is_primary=is_primary))

        return await asyncio.gather(*tasks, return_exceptions=True)
