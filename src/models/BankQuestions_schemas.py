from typing import List, Literal, Optional
from pydantic import BaseModel, Field

class Question(BaseModel):
    question_id: str = Field(..., description="Unique identifier for the question.")
    subtopic_id: str = Field(..., description="ID of the subtopic this question belongs to.")
    source_url: str = Field(..., description="URL of the source content from which the question was generated.")
    difficulty: Literal["easy", "medium", "hard"] = Field(..., description="Difficulty level of the question.")
    content: str = Field(..., description="The question text.")
    options: List[str] = Field(..., description="List of possible answers for multiple-choice questions.")
    correct_answer: str = Field(..., description="The correct answer to the question.")
    explanation: str = Field(..., description="Explanation for the correct answer.")

class QuizBank(BaseModel):
    quiz_id: str = Field(..., description="Unique identifier for the quiz bank.")
    subtopic_id: str = Field(..., description="ID of the subtopic this quiz bank belongs to.")
    questions: List[Question] = Field(..., description="List of questions in the quiz bank.")