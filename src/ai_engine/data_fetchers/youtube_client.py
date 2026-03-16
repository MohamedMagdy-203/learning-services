import re
import asyncio
import logging
from youtube_transcript_api import YouTubeTranscriptApi
from typing import Optional

logger = logging.getLogger(__name__)


def extract_video_id(url: str) -> Optional[str]:
    pattern = r"(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})"
    match = re.search(pattern, url)
    return match.group(1) if match else None


async def fetch_video_transcript(url: str) -> str:
    video_id = extract_video_id(url)
    if not video_id:
        logger.warning("Invalid YouTube URL: %s", url)
        return ""

    try:
        transcript_list = await asyncio.to_thread(  # type: ignore
            YouTubeTranscriptApi.get_transcript,  # type: ignore
            video_id,
            languages=["en", "ar"],  # type: ignore
        )

        full_text: str = " ".join([item["text"] for item in transcript_list])  # type: ignore
        logger.info("Successfully fetched transcript for video: %s", video_id)
        return full_text

    except Exception as exc:
        logger.warning("Could not fetch transcript for %s: %s", url, str(exc))
        return ""
