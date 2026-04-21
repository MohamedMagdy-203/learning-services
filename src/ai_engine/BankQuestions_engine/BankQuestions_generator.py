"""
BankQuestionsGenerator Module

This module is responsible for generating a quiz bank from retrieved content using an LLM.

- 70% of questions from primary source
- 30% from other sources
- Handles validation, errors, and deduplication
- Returns a structured quiz with unique questions
"""

import json
import asyncio
import uuid
import logging
import re
from typing import List

from openai import AsyncOpenAI
from pydantic import ValidationError
from langchain_core.documents import Document

from src.core.config import get_settings
from src.models.BankQuestions_schemas import Question
from src.ai_engine.llm_generators.BankQuestions_prompts import (
    get_bank_questions_generation_prompt,
)
from src.core.exceptions import (
    LLMGenerationError,
    InvalidLLMResponseError,
    EmptyContentError,
)

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

    async def _generate_for_source(
        self,
        documents: List[Document],
        source_url: str,
        subtopic_id: str,
        num_questions: int,
        difficulty_distribution: dict,
    ) -> List[Question]:
        if not documents:
            raise EmptyContentError("No content")

        prompt = get_bank_questions_generation_prompt(
            documents,
            num_questions,
            difficulty_distribution,
        )

        response = await self._call_llm_with_retry(prompt)
        content = response.choices[0].message.content

        try:
            data = json.loads(content)
        except json.JSONDecodeError:
            raise InvalidLLMResponseError("Invalid JSON")

        questions_data = data.get("questions", [])

        generated_questions = []

        for q_data in questions_data:
            try:
                question_obj = Question(
                    question_id=str(uuid.uuid4()),
                    subtopic_id=subtopic_id,
                    source_url=source_url,
                    difficulty=q_data.get("difficulty", "medium"),
                    content=q_data.get("content", ""),
                    options=q_data.get("options", []),
                    correct_answer=q_data.get("correct_answer"),
                    explanation=q_data.get("explanation", ""),
                )
                generated_questions.append(question_obj)

            except ValidationError:
                continue

        return generated_questions
