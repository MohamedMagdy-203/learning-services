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
        """
        Initialize the ContentDistiller.
        
        Creates and configures an AsyncOpenAI client using the GEMINI API key from application settings and sets a maximum prompt character limit of 100000 to reduce the risk of token overflow.
        """
        settings = get_settings()
        self.client = AsyncOpenAI(
            api_key=settings.GEMINI_API_KEY,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        )
        # Maximum character limit for the LLM prompt to avoid token overflow
        self.MAX_CHARS = 100000

    def _truncate_chunks(self, chunks: List[str]) -> List[str]:
        """
        Selects a prefix of the provided text chunks whose combined character count does not exceed the instance's MAX_CHARS.
        
        Parameters:
            chunks (List[str]): Ordered text chunks to consider.
        
        Returns:
            List[str]: A list containing the initial chunks whose total length is less than or equal to `self.MAX_CHARS`.
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
        Distills content for a single URL and returns a SingleDistilledItem.
        
        Retrieves text chunks for the given URL, produces a distilled representation using the configured LLM, and packages the result with the original URL and primary flag.
        
        Parameters:
            url (HttpUrl): The URL whose content will be distilled.
            is_primary (bool): When True, marks the returned item as the primary source.
        
        Returns:
            SingleDistilledItem: An object containing `url`, `distilled_content` (parsed into `DistilledContent`), and `is_primary`.
        
        Raises:
            DistillationError: If retrieval, distillation, parsing, or construction of the distilled result fails.
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
        Orchestrates concurrent distillation for a collection of URLs.
        
        Parameters:
            urls (List[HttpUrl]): Source URLs to distill.
            primary_url (Optional[HttpUrl]): If provided, the result whose URL string equals this value is marked as primary.
        
        Returns:
            List[Union[SingleDistilledItem, Exception]]: A list where successful entries are `SingleDistilledItem` objects and failed tasks are represented by the corresponding `Exception` instances.
        """
        tasks = []

        for url in urls:
            is_primary = (str(url) == str(primary_url)) if primary_url else False

            tasks.append(self._distill_single_url(url, is_primary=is_primary))

        # Execute all tasks in parallel. return_exceptions=True ensures one failure doesn't stop others.
        return await asyncio.gather(*tasks, return_exceptions=True)
