from fastapi import APIRouter, HTTPException, status
from src.ai_engine.distiller_engine.distiller import ContentDistiller
from src.models.distillation_schemas import ContentDistillationRequest,ContentDistillationResponse

dist_router = APIRouter(prefix="/api/v1/dist", tags=["distillation"])


@dist_router.post("/distill-content", response_model=ContentDistillationResponse, status_code=status.HTTP_200_OK)
async def distill_content(request: ContentDistillationRequest) -> ContentDistillationResponse:
    """
    Distills content from a given URL into key terms and main points.
    """
    distiller = ContentDistiller()
    result = await distiller.distill_content(request.url)

    if "error" in result:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result["error"])

    return ContentDistillationResponse(
        url=result["url"],
        distilled_content=result["distilled_content"]
    )