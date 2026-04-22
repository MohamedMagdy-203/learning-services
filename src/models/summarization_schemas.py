from pydantic import BaseModel, HttpUrl, Field
from typing import List, Dict, Optional


class SummarizationRequest(BaseModel):
    user_id: str
    subtopic_id: str
    urls: List[HttpUrl]
    subtopic_name: str
    subtopic_difficulty: Optional[str] = "Intermediate"
    primary_url: Optional[HttpUrl] = None
    urls: Optional[List[Optional[HttpUrl]]] = Field(default_factory=list)
    weaknesses: Optional[Dict[str, str]] = Field(default_factory=dict)


class SummarizationResponse(BaseModel):
    user_id: str
    subtopic_id: str
    primary_url: HttpUrl
    summary: str
