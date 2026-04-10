import json
import logging
import re
from src.models.schemas import MindmapNodeSchema

logger = logging.getLogger(__name__)


def parse_mindmap_response(raw_text: str) -> MindmapNodeSchema:
    """
    Safely parse the LLM JSON response into a validated MindmapNodeSchema.
    Strips markdown fences if present, then validates the structure.

    Args:
        raw_text: the raw string response from Gemini.

    Returns:
        A validated MindmapNodeSchema object.

    Raises:
        ValueError: if the response is not valid JSON or doesn't match
                    the expected mindmap structure.
    """
    text = raw_text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    text = text.strip()

    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        logger.error(
            "Failed to decode JSON from LLM response | error: %s | raw: %.200s",
            exc,
            raw_text,
        )
        raise ValueError("LLM response is not valid JSON") from exc

    try:
        mindmap = MindmapNodeSchema(**data)
    except Exception as exc:
        logger.error(
            "LLM response does not match MindmapNodeSchema | error: %s | data: %s",
            exc,
            data,
        )
        raise ValueError(
            "LLM response does not match expected mindmap structure"
        ) from exc

    logger.info(
        "Mindmap parsed successfully | root: %s | branches: %d",
        mindmap.topic,
        len(mindmap.children),
    )

    return mindmap