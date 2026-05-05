import logging
import json
import asyncio
from typing import List, Dict, Any
import re
from langchain_core.documents import Document
from openai import AsyncOpenAI
from openai import APIConnectionError, RateLimitError, APIStatusError
from src.ai_engine.vector_store.shared_retriever import retrieve_content_chunks
from src.ai_engine.summarization_engine.summarization_prompt import (
    build_summarization_prompt,
)
from src.core.config import Settings
from src.core.exceptions import NoContentFoundError
from src.core.messages import (
    SUMMARIZATION_START,
    SUMMARIZATION_INVOKE_LLM,
    SUMMARIZATION_SUCCESS,
    RETRIEVE_ERROR,
    NO_CONTENT_FOUND,
    LLM_INVOCATION_ERROR,
    NO_CONTENT_RESPONSE,
    RETRIEVE_FAILED_RESPONSE,
    LLM_FAILED_RESPONSE,
    AI_INVALID_JSON,
    AI_MISSING_SUMMARY,
)
from src.models.summarization_schemas import SummarizationRequest

logger = logging.getLogger(__name__)


class SummarizationService:
    def __init__(self, openai_client: AsyncOpenAI, settings: Settings):
        self.client = openai_client
        self.settings = settings
        self.model = settings.LLM_MODEL_NAME
        self.temperature = settings.LLM_TEMPERATURE
        self.max_retries = 2
        self.timeout = 30

    async def _call_llm_with_retry(self, prompt: str) -> str:
        for attempt in range(self.max_retries + 1):
            try:
                response = await asyncio.wait_for(
                    self.client.chat.completions.create(
                        model=self.model,
                        messages=[{"role": "user", "content": prompt}],
                        temperature=self.temperature,
                        response_format={"type": "json_object"},
                    ),
                    timeout=self.timeout,
                )
                return response.choices[0].message.content
            except (APIConnectionError, RateLimitError) as e:
                logger.warning(f"Transient LLM error (Attempt {attempt+1}): {e}")
                if attempt == self.max_retries:
                    raise
                await asyncio.sleep(1)
            except APIStatusError as e:
                if e.status_code == 429 or (500 <= e.status_code < 600):
                    logger.warning(
                        f"Transient LLM APIStatusError (Attempt {attempt+1}): HTTP {e.status_code}"
                    )
                    if attempt == self.max_retries:
                        raise
                    await asyncio.sleep(1)
                else:
                    logger.error(
                        f"Fatal LLM APIStatusError: HTTP {e.status_code} - {e.message}"
                    )
                    raise
            except Exception as e:
                logger.error(f"Fatal LLM error: {e}")
                raise

    async def summarize_content(
        self,
        request: SummarizationRequest,
        qdrant_client,
    ) -> Dict[str, Any]:
        """
        Main entry point for summarization logic.
        """
        primary_url = str(request.primary_url)
        logger.info(SUMMARIZATION_START, primary_url)

        try:
            documents: List[Document] = await retrieve_content_chunks(
                primary_url=primary_url,
                secondary_urls=[],
                client=qdrant_client,
                settings=self.settings,
            )

        except NoContentFoundError:
            logger.warning(NO_CONTENT_FOUND.format(url=primary_url))
            return {
                "user_id": request.user_id,
                "subtopic_id": request.subtopic_id,
                "primary_url": primary_url,
                "summary": NO_CONTENT_RESPONSE,
            }

        except Exception as e:
            logger.error(RETRIEVE_ERROR, primary_url, e)
            return {"error": RETRIEVE_FAILED_RESPONSE}

        prompt = build_summarization_prompt(
            documents=documents,
            subtopic_name=request.subtopic_name,
            subtopic_difficulty=request.subtopic_difficulty,
            weaknesses=request.weaknesses,
        )

        logger.info(SUMMARIZATION_INVOKE_LLM)

        try:
            content = await self._call_llm_with_retry(prompt)
            content = content.strip()
            content = re.sub(r"^`{3}(?:json)?\s*", "", content)
            content = re.sub(r"\s*`{3}$", "", content)

            try:
                result = json.loads(content)

                if (
                    not isinstance(result, dict)
                    or "summary" not in result
                    or not str(result["summary"]).strip()
                ):
                    logger.error(
                        f"{AI_MISSING_SUMMARY} - Content type: {type(content)}, Length: {len(content)}"
                    )
                    return {"error": LLM_FAILED_RESPONSE}

                summary_text = result["summary"]

            except json.JSONDecodeError:
                logger.error(
                    f"{AI_INVALID_JSON} - Content type: {type(content)}, Length: {len(content)}"
                )
                return {"error": LLM_FAILED_RESPONSE}

            logger.info(SUMMARIZATION_SUCCESS)

            return {
                "user_id": request.user_id,
                "subtopic_id": request.subtopic_id,
                "primary_url": primary_url,
                "summary": summary_text,
            }

        except Exception as e:
            logger.error(LLM_INVOCATION_ERROR, e, exc_info=True)
            return {"error": LLM_FAILED_RESPONSE}
