import json
import logging
import re
from typing import Any

logger = logging.getLogger(__name__)


def parse_reranker_response(raw_text: str) -> dict[str, Any]:
    """Safely parse the LLM JSON response, stripping markdown fences if present."""
    text = raw_text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    return json.loads(text.strip())


def enrich_with_raw_content(
    ranked_result: dict[str, Any],
    sources_by_url: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    """
    After the LLM picks the best sources by URL,
    look them up in the original cleaned_sources and attach their raw_content.
    """
    for key in ("best_course", "best_video", "best_blog"):
        item = ranked_result.get(key)
        if item is None:
            continue

        url = item.get("url", "")
        original = sources_by_url.get(url)

        if original:
            item["raw_content"] = original["raw_content"]
        else:
            # URL might have minor differences — try partial match as fallback
            matched = next(
                (
                    src
                    for src in sources_by_url.values()
                    if url in src["url"] or src["url"] in url
                ),
                None,
            )
            item["raw_content"] = matched["raw_content"] if matched else None
            if not matched:
                logger.warning("raw_content not found for %s | url: %s", key, url)

    return ranked_result
