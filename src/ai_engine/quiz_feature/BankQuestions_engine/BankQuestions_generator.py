"""
BankQuestionsGenerator Module

This module is responsible for generating a quiz bank from retrieved content using an LLM.

- 70% of questions from primary source
- 30% from other sources
- Handles validation, errors, and deduplication
- Returns a structured quiz with unique questions
"""

import json
import uuid
import re
import asyncio
import logging
from typing import List

from openai import AsyncOpenAI
from langchain_core.documents import Document
from pydantic import ValidationError

from src.models.quiz_schemas import Question, QuizBank

from src.core.config import get_settings
from src.core.exceptions import (
    NoContentFoundError,
    LLMGenerationError,
    InvalidLLMResponseError,
)

from src.core.messages import (
    NO_CONTENT_FOUND,
    NO_PRIMARY_DOCUMENTS_FOUND,
    NO_QUESTIONS_FOUND,
    INVALID_JSON,
    INVALID_FORMAT,
)

from src.ai_engine.quiz_feature.BankQuestions_prompts import (
    get_bank_questions_generation_prompt,
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
        bank_id: str,
    ) -> List[Question]:
        if num_questions <= 0:
            return []

        if not documents:
            raise NoContentFoundError(NO_CONTENT_FOUND.format(url=source_url))

        prompt = get_bank_questions_generation_prompt(
            documents,
            num_questions,
            difficulty_distribution,
        )

        response = await self._call_llm(prompt)
        content = response.choices[0].message.content

        if not content:
            raise InvalidLLMResponseError(
                NO_QUESTIONS_FOUND.format(source_url=source_url)
            )

        try:
            data = json.loads(content)
        except json.JSONDecodeError as e:
            raise InvalidLLMResponseError(INVALID_JSON) from e

        questions_data = data.get("questions")
        if not isinstance(questions_data, list):
            raise InvalidLLMResponseError(INVALID_FORMAT)

        generated_questions = []

        for q_data in questions_data:
            if not isinstance(q_data, dict):
                continue

            options = q_data.get("options", [])
            correct = q_data.get("correct_answer")
            difficulty = q_data.get("difficulty", "medium")
            explanations = q_data.get("explanations", {})

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
                    bank_id=bank_id,
                    source_url=source_url,
                    difficulty=difficulty,
                    content=q_data.get("content", ""),
                    options=options,
                    correct_answer=correct,
                    explanations=explanations,
                )

                generated_questions.append(question_obj)

            except ValidationError:
                continue

        return generated_questions

    async def generate_bank_questions(
        self,
        documents: List[Document],
        subtopic_id: str,
        primary_url: str,
        bank_id: str,
    ) -> QuizBank:
        TOTAL_QUESTIONS = self.settings.QUIZ_BANK_SIZE
        PRIMARY_SHARE = 0.7
        SECONDARY_SHARE_PER_SOURCE = 0.15

        primary_docs = [d for d in documents if d.metadata.get("is_primary")]
        if not primary_docs:
            raise NoContentFoundError(NO_PRIMARY_DOCUMENTS_FOUND)

        secondary_docs = [d for d in documents if not d.metadata.get("is_primary")]

        secondary_by_url = {}
        for doc in secondary_docs:
            url = doc.metadata.get("url")
            if url:
                secondary_by_url.setdefault(str(url), []).append(doc)

        primary_target = int(TOTAL_QUESTIONS * PRIMARY_SHARE)
        secondary_target = int(TOTAL_QUESTIONS * SECONDARY_SHARE_PER_SOURCE)

        tasks = [
            self._generate_for_source(
                primary_docs,
                primary_url,
                subtopic_id,
                primary_target,
                build_distribution(primary_target),
                bank_id=bank_id,
            )
        ]

        for url, docs in list(secondary_by_url.items())[:2]:
            tasks.append(
                self._generate_for_source(
                    docs,
                    url,
                    subtopic_id,
                    secondary_target,
                    build_distribution(secondary_target),
                    bank_id=bank_id,
                )
            )

        results = await asyncio.gather(*tasks, return_exceptions=True)

        all_questions = []
        for res in results:
            if not isinstance(res, Exception):
                all_questions.extend(res)

        seen = set()
        unique_questions = []

        for q in all_questions:
            key = normalize(q.content)
            if key not in seen:
                seen.add(key)
                unique_questions.append(q)

        while len(unique_questions) < TOTAL_QUESTIONS:
            missing = TOTAL_QUESTIONS - len(unique_questions)

            try:
                extra = await self._generate_for_source(
                    primary_docs,
                    primary_url,
                    subtopic_id,
                    missing,
                    build_distribution(missing),
                    bank_id=bank_id,
                )
            except (NoContentFoundError, InvalidLLMResponseError, LLMGenerationError):
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

        return QuizBank(
            bank_id=bank_id,
            subtopic_id=subtopic_id,
            questions=unique_questions[:TOTAL_QUESTIONS],
        )
