
import logging
import json
from typing import Dict, Any, List
from openai import OpenAI
from src.core.config import get_settings
from fastapi import HTTPException, status 
from src.ai_engine.data_fetchers.distillation_retrieval import retrieve_chunks_by_url
from src.ai_engine.llm_generators.distillation_prompts import get_distillation_prompt
from src.core.messages import NO_CONTENT_FOUND, DISTILLATION_JSON_ERROR, DISTILLATION_GENERAL_ERROR
from src.core.exceptions import NoContentFoundError, DistillationError

logger = logging.getLogger(__name__)

class ContentDistiller:
    def __init__(self):
        settings = get_settings()
       
        self.client = OpenAI(
            api_key=settings.GEMINI_API_KEY, 
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
         )
    async def distill_content(self, url: str) -> Dict[str, Any]:
        logger.info("Starting content distillation for URL: %s", url)



        chunks = retrieve_chunks_by_url(url)
        if not chunks:
           logger.warning("No chunks found for URL: %s", url)
           raise HTTPException(
           status_code=status.HTTP_404_NOT_FOUND,
           detail=NO_CONTENT_FOUND
         )

       
        distillation_prompt = get_distillation_prompt(chunks)
        try:
            distillation_response = self.client.chat.completions.create(
                model="gemini-2.0-flash", 
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that distills content into key terms, main points, and examples in JSON format."
                    },
                    {"role": "user", "content": distillation_prompt}
                ],
                response_format={"type": "json_object"}
            )

            distilled_content_str = distillation_response.choices[0].message.content
            distilled_content = json.loads(distilled_content_str)
            logger.info("Content distilled successfully for URL: %s", url)

        except json.JSONDecodeError as e:
            logger.error(
                "Error decoding JSON from LLM response for URL %s: %s\nResponse: %s",
                url, e, distilled_content_str
            )
            raise DistillationError(f"{DISTILLATION_JSON_ERROR}: {e}")

        except Exception as e:
            logger.error("Error during content distillation for URL %s: %s", url, e)
            raise DistillationError(f"{DISTILLATION_GENERAL_ERROR}: {e}")

        return {
            "url": url,
            "distilled_content": distilled_content
        }