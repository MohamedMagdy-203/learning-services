"""
BankQuestionsGenerator Module

This module is responsible for generating a quiz bank from distilled content using an LLM.

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
from typing import List, Dict, Any

from openai import AsyncOpenAI
from pydantic import ValidationError

from src.core.config import get_settings
from src.ai_engine.llm_generators.BankQuestions_prompts import (
    get_bank_questions_generation_prompt,
)

from src.models.BankQuestions_schemas import Question
from src.models.distillation_schemas import SingleDistilledItem, DistilledContent

from src.core.exceptions import (
    LLMGenerationError,
    InvalidLLMResponseError,
    EmptyContentError,
)

from src.core.messages import (
    INVALID_QUESTION_COUNT,
    EMPTY_SOURCE_CONTENT,
    NO_QUESTIONS_FOUND,
    LLM_API_ERROR,
    SKIP_QUESTION,
    INVALID_JSON,
    FEWER_EXPECTED_QUESTIONS,
)


logger = logging.getLogger(__name__)


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


class BankQuestionsGenerator:
    def __init__(self):
        settings = get_settings()
        self.client = AsyncOpenAI(
            api_key=settings.GEMINI_API_KEY,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        )

    async def _generate_for_source(
        self,
        distilled_content: DistilledContent,
        source_url: str,
        subtopic_id: str,
        num_questions: int,
        difficulty: str,
    ) -> List[Question]:
        if num_questions <= 0:
            raise LLMGenerationError(
                INVALID_QUESTION_COUNT.format(
                    num_questions=num_questions, source_url=source_url
                )
            )

        if not distilled_content or not distilled_content.main_points:
            raise EmptyContentError(EMPTY_SOURCE_CONTENT.format(source_url=source_url))

        prompt = get_bank_questions_generation_prompt(
            distilled_content, num_questions, difficulty
        )

        try:
            response = await self.client.chat.completions.create(
                model="gemini-2.0-flash",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
            )

            content = response.choices[0].message.content

            if not content:
                raise InvalidLLMResponseError(
                    NO_QUESTIONS_FOUND.format(source_url=source_url)
                )

            try:
                data = json.loads(content)
            except json.JSONDecodeError as e:
                raise InvalidLLMResponseError(INVALID_JSON) from e

            questions_data = (
                data.get("questions", data) if isinstance(data, dict) else data
            )

            if not isinstance(questions_data, list):
                raise InvalidLLMResponseError(
                    NO_QUESTIONS_FOUND.format(source_url=source_url)
                )

            generated_questions = []

            for q_data in questions_data:
                if not q_data.get("content") or not q_data.get("options"):
                    continue

                try:
                    question_obj = Question(
                        question_id=str(uuid.uuid4()),
                        subtopic_id=subtopic_id,
                        source_url=source_url,
                        difficulty=q_data.get("difficulty", difficulty),
                        content=q_data.get("content", ""),
                        options=q_data.get("options", []),
                        correct_answer=q_data.get("correct_answer", ""),
                        explanation=q_data.get("explanation", ""),
                    )
                    generated_questions.append(question_obj)

                except ValidationError as e:
                    logger.warning(SKIP_QUESTION.format(error=str(e)))
                    continue

            return generated_questions

        except Exception as e:
            logger.exception(f"LLM error for source: {source_url}")
            raise LLMGenerationError(
                LLM_API_ERROR.format(source_url=source_url, error=str(e))
            ) from e

    async def generate_bank_questions(
        self,
        distilled_results: List[SingleDistilledItem],
        subtopic_id: str,
        primary_url: str,
        total_questions: int,
    ) -> Dict[str, Any]:
        num_primary = round(total_questions * 0.7)
        num_others = total_questions - num_primary

        tasks = []

        # primary source
        primary_item = next((i for i in distilled_results if i.is_primary), None)

        if not primary_item:
            primary_item = next(
                (i for i in distilled_results if str(i.url) == str(primary_url)), None
            )

        if not primary_item:
            raise LLMGenerationError(f"Primary source not found: {primary_url}")

        tasks.append(
            self._generate_for_source(
                primary_item.distilled_content,
                str(primary_item.url),
                subtopic_id,
                num_primary,
                "medium",
            )
        )

        # other sources
        others = [i for i in distilled_results if not i.is_primary]

        if others and num_others > 0:
            for i, item in enumerate(others):
                count = num_others // len(others) + (
                    1 if i < num_others % len(others) else 0
                )

                if count <= 0:
                    continue

                tasks.append(
                    self._generate_for_source(
                        item.distilled_content,
                        str(item.url),
                        subtopic_id,
                        count,
                        "easy",
                    )
                )

        results = await asyncio.gather(*tasks, return_exceptions=True)

        all_questions = []

        for i, res in enumerate(results):
            if isinstance(res, Exception):
                if i == 0:
                    raise res
                logger.error(f"Error in source: {res}")
            else:
                all_questions.extend(res)

        if len(all_questions) < total_questions:
            logger.warning(FEWER_EXPECTED_QUESTIONS)

        clean_questions = [
            {
                "question_id": q.question_id,
                "subtopic_id": q.subtopic_id,
                "source_url": str(q.source_url),
                "difficulty": q.difficulty,
                "content": q.content,
                "options": q.options,
                "correct_answer": q.correct_answer,
                "explanation": q.explanation,
            }
            for q in all_questions
        ]

        seen = set()
        unique_questions = []

        for q in clean_questions:
            key = normalize(q["content"])
            if key not in seen:
                seen.add(key)
                unique_questions.append(q)

        return {
            "quiz_id": str(uuid.uuid4()),
            "subtopic_id": subtopic_id,
            "questions": unique_questions,
        }
