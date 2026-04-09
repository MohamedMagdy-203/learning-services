from fastapi import APIRouter
from src.services.summarizer import summarize_text

router = APIRouter()

from src.models.schemas import SummarizationRequest
@router.post("/summarize/")
def summarize_endpoint(request: SummarizationRequest):
    """
    Summarize technical content from a learning resource.
    """
    result = summarize_text(
        page_content=request.page_content,
        title=request.title,
        max_length=request.max_length,
        min_length=request.min_length
    )
    return {"summary": result}