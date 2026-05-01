import random
from typing import List, Optional, Set
from qdrant_client import AsyncQdrantClient
from qdrant_client.http.models import Filter, FieldCondition, MatchValue, MatchAny
from src.models.quiz_schemas import Question
import logging


logger = logging.getLogger(__name__)


class QuestionRetrieval:
    def __init__(self, client: AsyncQdrantClient, collection_name: str):
        self.client = client
        self.collection_name = collection_name

    async def get_question_by_bank(
        self,
        bank_id: str,
        difficulty: Optional[str] = None,
        exclude_ids: Optional[Set[str]] = None,
        limit: int = 15,
    ) -> Optional[Question]:
        must_conditions = [
            FieldCondition(
                key="bank_id",
                match=MatchValue(value=bank_id),
            )
        ]

        if difficulty:
            must_conditions.append(
                FieldCondition(
                    key="difficulty",
                    match=MatchValue(value=difficulty),
                )
            )

        must_not_conditions = []
        if exclude_ids:
            must_not_conditions.append(
                FieldCondition(
                    key="question_id",
                    match=MatchAny(any=list(exclude_ids)),
                )
            )

        result, _ = await self.client.scroll(
            collection_name=self.collection_name,
            scroll_filter=Filter(
                must=must_conditions,
                must_not=must_not_conditions,
            ),
            limit=limit,
            with_payload=True,
        )

        candidates: List[Question] = []

        for r in result:
            p = r.payload

            try:
                if not p:
                    logger.warning("Empty payload received from Qdrant")
                    continue

                candidates.append(
                    Question(
                        question_id=p["question_id"],
                        subtopic_id=p["subtopic_id"],
                        bank_id=p["bank_id"],
                        source_url=p["source_url"],
                        content=p["content"],
                        options=p["options"],
                        correct_answer=p["correct_answer"],
                        difficulty=p["difficulty"],
                        explanations=p.get("explanations", {}),
                        metadata=p.get("metadata", {}),
                    )
                )
            except KeyError as e:
                logger.warning("Missing field in Qdrant payload: %s | payload=%s", e, p)
                continue

            except Exception as e:
                logger.warning("Invalid Qdrant payload skipped: %s | payload=%s", e, p)
                continue

        if not candidates:
            return None

        return random.choice(candidates)
