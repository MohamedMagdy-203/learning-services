from pydantic import BaseModel, HttpUrl


class SummarizationRequest(BaseModel):
    user_id: str
    subtopic_id: str
    primary_url: HttpUrl


class SummarizationResponse(BaseModel):
    user_id: str
    subtopic_id: str
    primary_url: HttpUrl
    summary: str
