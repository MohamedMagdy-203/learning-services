from typing import List, Literal, Dict
from pydantic import BaseModel, Field, HttpUrl


class Question(BaseModel):
    question_id: str = Field(..., description="Unique identifier for the question.")
    subtopic_id: str = Field(
        ..., description="ID of the subtopic this question belongs to."
    )
    source_url: HttpUrl = Field(
        ...,
        description="URL of the source content from which the question was generated.",
    )
    difficulty: Literal["easy", "medium", "hard"] = Field(
        ..., description="Difficulty level of the question."
    )
    content: str = Field(..., description="The question text.")
    options: List[str] = Field(
        ...,
        description='List of possible answers (will be ["True", "False"] for True/False questions).',
    )
    correct_answer: str = Field(..., description="The correct answer to the question.")
    explanation: str = Field(..., description="Explanation for the correct answer.")


class QuizBank(BaseModel):
    quiz_id: str = Field(..., description="Unique identifier for the quiz bank.")
    subtopic_id: str = Field(
        ..., description="ID of the subtopic this quiz bank belongs to."
    )
    questions: List[Question] = Field(
        ..., description="List of questions in the quiz bank."
    )


class QuestionGenerationRequest(BaseModel):
    distilled_results: List[Dict] = Field(..., description="Distilled content results.")
    subtopic_id: str = Field(..., description="Subtopic ID.")
    primary_url: HttpUrl = Field(..., description="Primary source URL.")
    total_questions: int = Field(30, description="Total questions to generate.")
