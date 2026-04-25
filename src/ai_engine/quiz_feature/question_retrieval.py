import random
from typing import List, Optional, Set
from qdrant_client import AsyncQdrantClient
from qdrant_client.http.models import Filter, FieldCondition, MatchValue
from src.models.quiz_schemas import Question


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

        result, _ = await self.client.scroll(
            collection_name=self.collection_name,
            scroll_filter=Filter(must=must_conditions),
            limit=limit,
            with_payload=True,
        )

        candidates: List[Question] = []

        for r in result:
            p = r.payload

            if exclude_ids and p["question_id"] in exclude_ids:
                continue

            try:
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
            except Exception:
                continue

        if not candidates:
            return None

        return random.choice(candidates)
