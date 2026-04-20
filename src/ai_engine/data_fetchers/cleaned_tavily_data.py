from typing import Dict, Any
from src.core.config import Settings
from src.models.schemas import RoadmapGenerationRequest
from src.ai_engine.data_fetchers.tavily_client import fetch_subtopic_content
from src.ai_engine.data_fetchers.data_cleaner import clean_content


async def fetch_and_clean_subtopic_content(
    settings: Settings,
    requested_data: RoadmapGenerationRequest,
) -> list[Dict[str, Any]]:
    raw_results = await fetch_subtopic_content(
        settings=settings,
        requested_data=requested_data,
    )

    cleaned_results = []
    for result in raw_results.get("results", []):
        raw_text = result.get("raw_content", "")

        if not raw_text or len(raw_text.strip()) < 50:
            continue

        cleaned_content = clean_content(raw_text)
        cleaned_results.append(
            {
                "title": result.get("title", ""),
                "url": result.get("url", ""),
                "raw_content": cleaned_content,
            }
        )

    return cleaned_results
