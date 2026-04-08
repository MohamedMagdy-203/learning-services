from pydantic import BaseModel, Field
from typing import List, Dict


class ContentDistillationRequest(BaseModel):
    url: str = Field(..., description="The URL of the content to distill.")


class KeyTerm(BaseModel):
    term: str = Field(..., description="The key term or concept extracted from the content.")
    definition: str = Field(..., description="The definition or explanation of the key term.")


class DistilledContent(BaseModel):
    key_terms: List[KeyTerm] = Field(..., description="List of extracted key terms with their definitions.")
    main_points: List[str] = Field(..., description="List of main points or summary highlights extracted from the content.")
    examples: List[str] = Field([], description="Optional illustrative examples extracted from the content to aid understanding.")


class ContentDistillationResponse(BaseModel):
    url: str = Field(..., description="The URL of the processed content.")
    distilled_content: DistilledContent = Field(..., description="The structured distilled content including key terms, main points, and examples.")