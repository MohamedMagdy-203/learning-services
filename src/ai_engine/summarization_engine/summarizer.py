import logging
import json
import asyncio
from typing import List, Dict, Any

from langchain_core.documents import Document
from openai import AsyncOpenAI

from src.ai_engine.llm_generators.summarization_prompt import build_summarization_prompt
from src.ai_engine.data_fetchers.chunks_retrieval import retrieve_chunks_by_url
from src.core.config import Settings
from src.core.exceptions import NoContentFoundError
from src.core.messages import (
    SUMMARIZATION_START,
    SUMMARIZATION_INVOKE_LLM,
    SUMMARIZATION_SUCCESS,
    RETRIEVE_ERROR,
    NO_CONTENT_WARNING,
    LLM_INVOCATION_ERROR,
    NO_CONTENT_RESPONSE,
    RETRIEVE_FAILED_RESPONSE,
    LLM_FAILED_RESPONSE,
    AI_INVALID_JSON,
    AI_MISSING_SUMMARY,
)

logger = logging.getLogger(__name__)


class SummarizationService:
    def __init__(self, openai_client: AsyncOpenAI, settings: Settings):
        """
        Inject the shared OpenAI client and settings.
        This ensures we don't recreate connections per request.
        """
        self.client = openai_client
        self.settings = settings

        self.model = settings.LLM_MODEL_NAME
        self.temperature = settings.LLM_TEMPERATURE

        self.max_retries = 2
        self.timeout = 30

    async def _call_llm_with_retry(self, prompt: str) -> str:
        """
        Calls the LLM with a retry mechanism and timeout.
        """
        for attempt in range(self.max_retries + 1):
            try:
                response = await asyncio.wait_for(
                    self.client.chat.completions.create(
                        model=self.model,
                        messages=[{"role": "user", "content": prompt}],
                        temperature=self.temperature,
                    ),
                    timeout=self.timeout,
                )

                return response.choices[0].message.content

            except Exception as e:
                logger.warning(f"LLM attempt {attempt + 1} failed: {e}")

                if attempt == self.max_retries:
                    raise

                await asyncio.sleep(1)

    async def summarize_content(
        self,
        user_id: str,
        subtopic_id: str,
        primary_url: str,
        qdrant_client,
    ) -> Dict[str, Any]:
        """
        Main entry point for summarization logic.
        Retrieves chunks, builds prompt, calls LLM, and validates output.
        """
        logger.info(SUMMARIZATION_START, primary_url)

        try:
            documents: List[Document] = await retrieve_chunks_by_url(
                primary_url=primary_url, client=qdrant_client, settings=self.settings
            )

        except NoContentFoundError:
            logger.warning(NO_CONTENT_WARNING, primary_url)
            return {
                "user_id": user_id,
                "subtopic_id": subtopic_id,
                "primary_url": primary_url,
                "summary": NO_CONTENT_RESPONSE,
            }

        except Exception as e:
            logger.error(RETRIEVE_ERROR, primary_url, e)
            return {"error": RETRIEVE_FAILED_RESPONSE}

        prompt = build_summarization_prompt(documents)

        logger.info(SUMMARIZATION_INVOKE_LLM)

        try:
            content = await self._call_llm_with_retry(prompt)

            try:
                result = json.loads(content)

                if (
                    not isinstance(result, dict)
                    or "summary" not in result
                    or not str(result["summary"]).strip()
                ):
                    logger.error(AI_MISSING_SUMMARY, content)
                    return {"error": LLM_FAILED_RESPONSE}

                summary_text = result["summary"]

            except json.JSONDecodeError:
                logger.error(AI_INVALID_JSON, content)
                return {"error": LLM_FAILED_RESPONSE}

            logger.info(SUMMARIZATION_SUCCESS)

            return {
                "user_id": user_id,
                "subtopic_id": subtopic_id,
                "primary_url": primary_url,
                "summary": summary_text,
            }

        except Exception as e:
            logger.error(LLM_INVOCATION_ERROR, e, exc_info=True)
            return {"error": LLM_FAILED_RESPONSE}
