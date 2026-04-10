import logging
from fastapi import APIRouter, Depends, HTTPException, status
from src.models.distillation_schemas import (
    ContentDistillationRequest,
    ContentDistillationResponse,
)
from src.ai_engine.distiller_engine.distiller import ContentDistiller
from src.core.messages import PRIMARY_SOURCE_REQUIRED_ERROR, NO_CONTENT_DISTILLED_ERROR

logger = logging.getLogger(__name__)

dist_router = APIRouter(prefix="/api/v1/dist", tags=["distillation"])

_distiller = ContentDistiller()


def get_distiller() -> ContentDistiller:
    return _distiller


@dist_router.post("/distill-content", response_model=ContentDistillationResponse)
async def distill_content(
    request: ContentDistillationRequest,
    distiller: ContentDistiller = Depends(get_distiller),
):
    results = await distiller.distill_multiple_urls(
        urls=request.urls, primary_url=request.primary_url
    )

    final_results = [res for res in results if not isinstance(res, Exception)]

    for res in results:
        if isinstance(res, Exception):
            logger.error(f"Distillation task failed: {str(res)}")

    if request.primary_url:
        primary_exists = any(
            str(item.url) == str(request.primary_url) for item in final_results
        )

        if not primary_exists:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=PRIMARY_SOURCE_REQUIRED_ERROR.format(url=request.primary_url),
            )

    if not final_results:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=NO_CONTENT_DISTILLED_ERROR
        )

    return ContentDistillationResponse(results=final_results)
