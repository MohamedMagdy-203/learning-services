"""
BankQuestionsGenerator Module

This module is responsible for generating a quiz bank from retrieved content using an LLM.

- 70% of questions from primary source
- 30% from other sources
- Handles validation, errors, and deduplication
- Returns a structured quiz with unique questions
"""

import asyncio
import json
import logging
import re
import uuid
from typing import List
from langchain_core.documents import Document
from openai import AsyncOpenAI
from pydantic import ValidationError

from src.ai_engine.llm_generators.BankQuestions_prompts import (
    get_bank_questions_generation_prompt,
)
from src.core.config import get_settings
from src.core.exceptions import (
    NoContentFoundError,
    InvalidLLMResponseError,
    LLMGenerationError,
)
from src.core.messages import (
    FALLBACK_ATTEMPT_FAILED,
    FALLBACK_TRIGGERED,
    INVALID_JSON,
    LLM_API_ERROR,
    NO_CONTENT_FOUND,
    NO_PRIMARY_DOCUMENTS_FOUND,
    NO_QUESTIONS_FOUND,
    SECONDARY_SOURCE_FAILED,
    SKIP_QUESTION,
    UNABLE_TO_REACH_TARGET,
)
from src.models.BankQuestions_schemas import Question, QuizBank

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

    async def _call_llm(self, prompt: str):
        try:
            return await self.client.chat.completions.create(
                model=self.settings.LLM_MODEL_NAME,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                temperature=self.settings.LLM_TEMPERATURE,
            )

        except Exception as e:
            logger.exception("LLM request failed")
            raise LLMGenerationError(str(e)) from e

    async def _generate_for_source(
        self,
        documents: List[Document],
        source_url: str,
        subtopic_id: str,
        num_questions: int,
        difficulty_distribution: dict,
    ) -> List[Question]:
        if num_questions <= 0:
            # Return empty list if no questions are requested
            return []

        if not documents:
            raise NoContentFoundError(NO_CONTENT_FOUND.format(url=source_url))

        prompt = get_bank_questions_generation_prompt(
            documents,
            num_questions,
            difficulty_distribution,
        )

        try:
            response = await self._call_llm(prompt)
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
            logger.exception(
                "LLM error while generating from %s",
                source_url,
            )

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
        TOTAL_QUESTIONS = 100
        PRIMARY_SHARE = 0.7
        SECONDARY_SHARE_PER_SOURCE = 0.15

        primary_docs = [d for d in documents if d.metadata.get("is_primary")]

        if not primary_docs:
            raise NoContentFoundError(NO_PRIMARY_DOCUMENTS_FOUND)

        secondary_docs = [d for d in documents if not d.metadata.get("is_primary")]

        secondary_by_url: dict[str, List[Document]] = {}

        for i, doc in enumerate(secondary_docs):
            url = doc.metadata.get("url")

            if not url:
                logger.warning(
                    f"Skipping secondary doc at index {i} " "due to missing URL"
                )
                continue

            secondary_by_url.setdefault(str(url), []).append(doc)

        primary_target_count = int(TOTAL_QUESTIONS * PRIMARY_SHARE)
        secondary_target_count_per_source = int(
            TOTAL_QUESTIONS * SECONDARY_SHARE_PER_SOURCE
        )

        tasks = []
        primary_questions_to_request = primary_target_count

        # Primary source task
        tasks.append(
            self._generate_for_source(
                primary_docs,
                primary_url,
                subtopic_id,
                primary_questions_to_request,
                build_distribution(primary_questions_to_request),
            )
        )

        # Secondary sources tasks (limit to 2 as per original logic, but make it more robust)
        secondary_urls_to_process = list(secondary_by_url.items())[:2]
        for url, docs_for_url in secondary_urls_to_process:
            tasks.append(
                self._generate_for_source(
                    docs_for_url,
                    url,
                    subtopic_id,
                    secondary_target_count_per_source,
                    build_distribution(secondary_target_count_per_source),
                )
            )

        results = await asyncio.gather(
            *tasks,
            return_exceptions=True,
        )

        primary_result = results[0]
        secondary_results = results[1:]

        all_questions = []
        if isinstance(primary_result, Exception):
            logger.error(f"Primary source generation failed: {primary_result}")

            raise primary_result
        else:
            all_questions.extend(primary_result)

        questions_from_secondary_sources = 0
        for i, res in enumerate(secondary_results):
            if isinstance(res, Exception):
                logger.warning(
                    SECONDARY_SOURCE_FAILED.format(
                        index=i,
                        error=str(res),
                    )
                )

            else:
                all_questions.extend(res)
                questions_from_secondary_sources += len(res)

        seen = set()
        unique_questions = []

        for q in all_questions:
            key = normalize(q.content)

            if key not in seen:
                seen.add(key)
                unique_questions.append(q)

        attempts = 0
        max_attempts = 3

        # Fallback mechanism to reach TOTAL_QUESTIONS using primary source
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
                logger.warning(
                    FALLBACK_ATTEMPT_FAILED.format(
                        attempt=attempts,
                        error=str(e),
                    )
                )
                break

            added = 0

            for q in extra:
                key = normalize(q.content)

                if key not in seen:
                    seen.add(key)
                    unique_questions.append(q)
                    added += 1

            if added == 0:
                break

        if len(unique_questions) < TOTAL_QUESTIONS:
            logger.warning(
                UNABLE_TO_REACH_TARGET.format(
                    current=len(unique_questions),
                    target=TOTAL_QUESTIONS,
                )
            )

        unique_questions = unique_questions[:TOTAL_QUESTIONS]

        return QuizBank(
            quiz_id=str(uuid.uuid4()),
            subtopic_id=subtopic_id,
            questions=unique_questions,
        )
