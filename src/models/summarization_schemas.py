from pydantic import BaseModel, HttpUrl
from typing import List, Dict


class SummarizationRequest(BaseModel):
    user_id: str
    subtopic_id: str
    urls: List[HttpUrl]
    primary_url: HttpUrl
    subtopic_name: str
    subtopic_difficulty: str
    weaknesses: Dict[str, str]


class SummarizationResponse(BaseModel):
    user_id: str
    subtopic_id: str
    primary_url: HttpUrl
    summary: str
