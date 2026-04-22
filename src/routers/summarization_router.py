import logging
from fastapi import APIRouter, Depends
from fastapi import HTTPException
from src.ai_engine.summarization_engine.summarizer import SummarizationService
from src.models.summarization_schemas import (
    SummarizationRequest,
    SummarizationResponse,
)

from src.ai_engine.data_fetchers.qdrant_client_dependency import (
    get_qdrant_client_dependency,
)
from src.ai_engine.summarization_engine.openai_client_dependency import (
    get_openai_client,
)

from src.core.config import get_settings, Settings

logger = logging.getLogger(__name__)

summ_router = APIRouter(prefix="/api/v1/summarize", tags=["summarization"])


def get_summarization_service(
    openai_client=Depends(get_openai_client), settings: Settings = Depends(get_settings)
) -> SummarizationService:
    return SummarizationService(openai_client=openai_client, settings=settings)


@summ_router.post("/generate", response_model=SummarizationResponse)
async def generate_summary(
    request: SummarizationRequest,
    qdrant_client=Depends(get_qdrant_client_dependency),
    service: SummarizationService = Depends(get_summarization_service),
):
    result = await service.summarize_content(
        request=request,
        qdrant_client=qdrant_client,
    )
    if "error" in result:
        raise HTTPException(
            status_code=502,
            detail=result["error"],
        )
    return result
