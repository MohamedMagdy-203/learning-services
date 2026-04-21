"""
BankQuestionsGenerator Module

This module is responsible for generating a quiz bank from retrieved content using an LLM.

- 70% of questions from primary source
- 30% from other sources
- Handles validation, errors, and deduplication
- Returns a structured quiz with unique questions
"""

import asyncio
import logging
import re

from openai import AsyncOpenAI

from src.core.config import get_settings
from src.core.exceptions import LLMGenerationError

logger = logging.getLogger(__name__)


def normalize(text: str) -> str:
    text = re.sub(r"[^\w\s]", "", text)
    return re.sub(r"\s+", " ", text.strip().lower())


class BankQuestionsGenerator:
    def __init__(self, client: AsyncOpenAI):
        self.client = client
        self.settings = get_settings()

    async def _call_llm_with_retry(self, prompt: str, retries: int = 3):
        for attempt in range(retries):
            try:
                response = await asyncio.wait_for(
                    self.client.chat.completions.create(
                        model=self.settings.LLM_MODEL_NAME,
                        messages=[{"role": "user", "content": prompt}],
                        response_format={"type": "json_object"},
                        temperature=self.settings.LLM_TEMPERATURE,
                    ),
                    timeout=30,
                )
                return response

            except Exception as e:
                logger.warning(f"LLM error (attempt {attempt+1}): {e}")
                await asyncio.sleep(2**attempt)

        raise LLMGenerationError("LLM failed after retries")
