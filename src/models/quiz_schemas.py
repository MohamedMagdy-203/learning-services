from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, HttpUrl, model_validator
from src.core.messages import PRIMARY_URL_NOT_IN_URLS


class Question(BaseModel):
    question_id: str
    subtopic_id: str
    bank_id: str
    source_url: HttpUrl
    content: str
    options: List[str]
    correct_answer: str
    difficulty: Optional[str] = "Intermediate"
    explanations: Dict[str, str]
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_correct_answer_in_options(self):
        if self.correct_answer not in self.options:
            raise ValueError("correct_answer must be one of options")
        return self


class QuizBank(BaseModel):
    bank_id: str
    subtopic_id: str
    questions: List[Question]


class QuestionGenerationRequest(BaseModel):
    user_id: str
    subtopic_id: str
    urls: List[HttpUrl]
    primary_url: HttpUrl
    subtopic_name: str
    subtopic_difficulty: Optional[str] = "Intermediate"
    weaknesses: Optional[Dict[str, str]]

    @model_validator(mode="after")
    def validate_primary_url(self):
        if self.primary_url not in self.urls:
            raise ValueError(PRIMARY_URL_NOT_IN_URLS)
        return self


class StartQuizRequest(BaseModel):
    bank_id: str = Field(..., min_length=1)
    user_id: str = Field(..., min_length=1)


class SubmitAnswerRequest(BaseModel):
    session_id: str
    question_id: str
    is_correct: bool
    response_time: float = Field(..., ge=0)
