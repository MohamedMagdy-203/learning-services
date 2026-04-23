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
from src.models.BankQuestions_schemas import Question, QuizBank
from src.ai_engine.llm_generators.BankQuestions_prompts import (
    get_bank_questions_generation_prompt,
)

from src.core.exceptions import (
    LLMGenerationError,
    InvalidLLMResponseError,
    EmptyContentError,
)

from src.core.messages import (
    INVALID_QUESTION_COUNT,
    NO_QUESTIONS_FOUND,
    LLM_API_ERROR,
    SKIP_QUESTION,
    INVALID_JSON,
    NO_CONTENT_FOUND,
    FALLBACK_TRIGGERED,
    LLM_TIMEOUT,
    LLM_RETRY_ERROR,
    SECONDARY_SOURCE_FAILED,
    LESS_THAN_TWO_SECONDARY,
)

logger = logging.getLogger(__name__)


def normalize(text: str) -> str:
    text = re.sub(r"[^\w\s]", "", text)
    return re.sub(r"\s+", " ", text.strip().lower())


def build_distribution(total: int) -> dict:
    easy = total // 3
    medium = total // 3
    hard = total - easy - medium
    return {"easy": easy, "medium": medium, "hard": hard}


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

            except asyncio.TimeoutError:
                logger.warning(LLM_TIMEOUT.format(attempt=attempt + 1))

            except Exception as e:
                logger.warning(
                    LLM_RETRY_ERROR.format(
                        attempt=attempt + 1,
                        error=str(e),
                    )
                )

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
        if num_questions <= 0:
            raise LLMGenerationError(
                INVALID_QUESTION_COUNT.format(
                    num_questions=num_questions,
                    source_url=source_url,
                )
            )

        if not documents:
            raise EmptyContentError(NO_CONTENT_FOUND.format(url=source_url))

        prompt = get_bank_questions_generation_prompt(
            documents,
            num_questions,
            difficulty_distribution,
        )

        try:
            response = await self._call_llm_with_retry(prompt)

            content = response.choices[0].message.content

            if not content:
                raise InvalidLLMResponseError(
                    NO_QUESTIONS_FOUND.format(source_url=source_url)
                )

            try:
                data = json.loads(content)
            except json.JSONDecodeError:
                logger.error(INVALID_JSON)
                raise InvalidLLMResponseError(INVALID_JSON)

            questions_data = data.get("questions")

            if not isinstance(questions_data, list):
                raise InvalidLLMResponseError(
                    NO_QUESTIONS_FOUND.format(source_url=source_url)
                )

            generated_questions = []

            for q_data in questions_data:
                if not isinstance(q_data, dict):
                    logger.warning(
                        SKIP_QUESTION.format(error="Question item is not an object")
                    )
                    continue

                options = q_data.get("options", [])
                correct = q_data.get("correct_answer")
                difficulty = q_data.get("difficulty", "medium")

                if not q_data.get("content"):
                    continue

                if not options or len(options) < 2:
                    continue

                if correct not in options:
                    continue

                if difficulty not in {"easy", "medium", "hard"}:
                    continue

                try:
                    question_obj = Question(
                        question_id=str(uuid.uuid4()),
                        subtopic_id=subtopic_id,
                        source_url=source_url,
                        difficulty=difficulty,
                        content=q_data.get("content", ""),
                        options=options,
                        correct_answer=correct,
                        explanation=q_data.get("explanation", ""),
                    )

                    generated_questions.append(question_obj)

                except ValidationError as e:
                    logger.warning(SKIP_QUESTION.format(error=str(e)))
                    continue

            return generated_questions

        except ValidationError:
            raise
        except InvalidLLMResponseError:
            raise
        except Exception as e:
            logger.exception(f"LLM error while generating from {source_url}")
            raise LLMGenerationError(
                LLM_API_ERROR.format(
                    source_url=source_url,
                    error=str(e),
                )
            ) from e

    async def generate_bank_questions(
        self,
        documents: List[Document],
        subtopic_id: str,
        primary_url: str,
    ) -> QuizBank:
        TOTAL_QUESTIONS = 30

        primary_docs = [d for d in documents if d.metadata.get("is_primary")]
        if not primary_docs:
            raise EmptyContentError("No primary documents found")

        secondary_docs = [d for d in documents if not d.metadata.get("is_primary")]

        if len(secondary_docs) < 2:
            logger.warning(LESS_THAN_TWO_SECONDARY)

        primary_dist = {"easy": 7, "medium": 7, "hard": 7}
        secondary_dist = {"easy": 2, "medium": 2, "hard": 1}

        primary_task = self._generate_for_source(
            primary_docs,
            primary_url,
            subtopic_id,
            21,
            primary_dist,
        )

        secondary_tasks = []

        for i, doc in enumerate(secondary_docs[:2]):
            url = doc.metadata.get("url")

            if not url:
                logger.warning(
                    f"Skipping secondary doc at index {i} due to missing URL"
                )
                continue

            secondary_tasks.append(
                self._generate_for_source(
                    [doc],
                    url,
                    subtopic_id,
                    5,
                    secondary_dist,
                )
            )

        results = await asyncio.gather(
            primary_task,
            *secondary_tasks,
            return_exceptions=True,
        )

        primary_result = results[0]

        if isinstance(primary_result, Exception):
            raise primary_result

        secondary_results = results[1:]

        all_questions = []
        all_questions.extend(primary_result)

        for i, res in enumerate(secondary_results):
            if isinstance(res, Exception):
                logger.warning(
                    SECONDARY_SOURCE_FAILED.format(
                        index=i,
                        error=str(res),
                    )
                )
                continue
            all_questions.extend(res)

        seen = set()
        unique_questions = []

        for q in all_questions:
            key = normalize(q.content + "".join(sorted(q.options)))
            if key not in seen:
                seen.add(key)
                unique_questions.append(q)
        attempts = 0
        max_attempts = 3

        while len(unique_questions) < TOTAL_QUESTIONS and attempts < max_attempts:
            attempts += 1

            missing = TOTAL_QUESTIONS - len(unique_questions)

            logger.warning(FALLBACK_TRIGGERED.format(missing=missing))

            fallback_dist = build_distribution(missing)

            try:
                extra = await self._generate_for_source(
                    primary_docs,
                    primary_url,
                    subtopic_id,
                    missing,
                    fallback_dist,
                )
            except Exception as e:
                logger.warning(f"Fallback attempt {attempts} failed: {str(e)}")
                break

            added = 0

            for q in extra:
                key = normalize(q.content + "".join(sorted(q.options)))
                if key not in seen:
                    seen.add(key)
                    unique_questions.append(q)
                    added += 1

            if added == 0:
                break

        if len(unique_questions) < TOTAL_QUESTIONS and unique_questions:
            logger.warning("Force filling to reach TOTAL_QUESTIONS")
            while len(unique_questions) < TOTAL_QUESTIONS:
                unique_questions.append(unique_questions[0])

        unique_questions = unique_questions[:TOTAL_QUESTIONS]

        return QuizBank(
            quiz_id=str(uuid.uuid4()),
            subtopic_id=subtopic_id,
            questions=unique_questions,
        )
