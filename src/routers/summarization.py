from fastapi import APIRouter
from src.services.summarizer import summarize_text, fetch_context_from_qdrant
from src.models.schemas import SummarizationRequest
import asyncio

summarization_router = APIRouter()


@summarization_router.post("/summarize/")
async def summarize_endpoint(request: SummarizationRequest):
    
    loop = asyncio.get_running_loop()

    fetched_context = await loop.run_in_executor(
        None,
        fetch_context_from_qdrant,
        request.title
    )


    result = await loop.run_in_executor(
        None,
        summarize_text,
        fetched_context,
        request.page_content,
        request.title,
        request.max_length,
        request.min_length
    )

    return {"summary": result}
