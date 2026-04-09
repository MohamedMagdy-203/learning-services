from fastapi import APIRouter
from src.services.summarizer import summarize_text
from src.models.schemas import SummarizationRequest

router = APIRouter()


@summarization_router.post("/summarize/")
async def summarize_endpoint(request: SummarizationRequest):
    import asyncio
    
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(
        None,
        summarize_text,
        request.page_content,
        request.title,
        request.max_length,
        request.min_length
    )

    return {"summary": result}