from typing import List, Optional
from pydantic import BaseModel, HttpUrl, Field


class ContentDistillationRequest(BaseModel):
    urls: List[HttpUrl] = Field(
        ..., description="List of URLs of the content to distill."
    )
    primary_url: Optional[HttpUrl] = Field(
        None, description="Optional: The primary URL for quiz weighting."
    )


class KeyTerm(BaseModel):
    term: str = Field(..., description="The key term or concept.")
    definition: str = Field(..., description="The definition of the key term.")


class DistilledContent(BaseModel):
    key_terms: List[KeyTerm] = Field(..., description="List of extracted key terms.")
    main_points: List[str] = Field(..., description="List of main points.")
    examples: List[str] = Field([], description="Optional illustrative examples.")


class SingleDistilledItem(BaseModel):
    url: HttpUrl = Field(..., description="The URL of the processed content.")
    distilled_content: DistilledContent = Field(
        ..., description="The structured distilled content."
    )
    is_primary: bool = Field(
        False, description="Flag indicating if this is the primary source."
    )


class ContentDistillationResponse(BaseModel):
    results: List[SingleDistilledItem] = Field(
        ..., description="List of distilled content per URL."
    )
