from typing import List
from qdrant_client import AsyncQdrantClient
from qdrant_client.http.models import PointStruct
from src.models.quiz_schemas import Question


class QdrantQuestionStore:
    def __init__(self, client: AsyncQdrantClient, collection_name: str):
        self.client = client
        self.collection_name = collection_name

    async def store_questions(
        self,
        questions: List[Question],
        bank_id: str,
    ):
        points = []

        for q in questions:
            payload = {
                "question_id": q.question_id,
                "bank_id": bank_id,
                "subtopic_id": q.subtopic_id,
                "source_url": str(q.source_url),
                "content": q.content,
                "options": q.options,
                "correct_answer": q.correct_answer,
                "difficulty": q.difficulty,
                "explanations": q.explanations,
                "metadata": q.metadata,
            }

            points.append(
                PointStruct(
                    id=q.question_id,
                    vector=[0.0],
                    payload=payload,
                )
            )

        await self.client.upsert(
            collection_name=self.collection_name,
            points=points,
        )
