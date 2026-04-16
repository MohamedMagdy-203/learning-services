import logging
from google.genai import types
from google import genai
from src.core.config import get_settings
from src.models.schemas import MindmapGenerationRequest, MindmapNodeSchema
from src.ai_engine.mindmap_feature.mindmap_prompt import build_mindmap_prompt
from src.ai_engine.mindmap_feature.mindmap_parser import parse_mindmap_response

# from src.ai_engine.mindmap.mindmap_generator import generate_mindmap as run_mindmap_generation

logger = logging.getLogger(__name__)

_client: genai.Client | None = None


def _get_client() -> genai.Client:
    global _client
    if _client is None:
        _client = genai.Client(
            api_key=get_settings().GEMINI_API_KEY,
            http_options=types.HttpOptions(timeout=60000),
        )
    return _client


async def generate_mindmap(
    request: MindmapGenerationRequest,
    chunks: list[str],
) -> MindmapNodeSchema:
    """
    Build the prompt, call Gemini, and return a validated MindmapNodeSchema.

    Args:
        request: the full mindmap generation request (subtopic + weaknesses).
        chunks:  combined content chunks from all available sources.

    Returns:
        A validated MindmapNodeSchema tree.

    Raises:
        ValueError: if Gemini returns an empty response or invalid JSON/structure.
    """
    prompt = build_mindmap_prompt(request=request, chunks=chunks)

    logger.info(
        "Calling Gemini for mindmap generation | subtopic: %s | chunks: %d",
        request.subtopic_name,
        len(chunks),
    )

    response = await _get_client().aio.models.generate_content(  # type: ignore
        model="gemini-3-flash-preview",
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.2,
            max_output_tokens=8192,
            response_mime_type="application/json",
        ),
    )

    if not response.text:
        logger.error(
            "Gemini returned empty response | subtopic: %s",
            request.subtopic_name,
        )
        raise ValueError("Gemini returned an empty response")

    mindmap = parse_mindmap_response(response.text)

    logger.info(
        "Mindmap generated | subtopic: %s | branches: %d",
        request.subtopic_name,
        len(mindmap.children),
    )

    return mindmap
