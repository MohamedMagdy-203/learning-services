from typing import List, Literal, Dict
from pydantic import BaseModel, Field, HttpUrl, model_validator
from src.core.messages import PRIMARY_URL_NOT_IN_URLS


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
    user_id: str = Field(..., description="ID of the user.")
    subtopic_id: str = Field(..., description="ID of the subtopic.")

    urls: List[HttpUrl] = Field(..., description="List of source URLs.")
    primary_url: HttpUrl = Field(..., description="Primary selected URL.")

    subtopic_name: str = Field(..., description="Name of the subtopic.")
    subtopic_difficulty: str = Field(..., description="Difficulty level as string.")

    weaknesses: Dict[str, str] = Field(
        default_factory=dict, description="User weaknesses per concept."
    )

    @model_validator(mode="after")
    def validate_primary_url(self):
        if self.primary_url not in self.urls:
            raise ValueError(PRIMARY_URL_NOT_IN_URLS)
        return self
