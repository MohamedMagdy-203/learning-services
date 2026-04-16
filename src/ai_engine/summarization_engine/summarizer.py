import logging

from src.core.config import Settings

logger = logging.getLogger(__name__)


class SummarizationService:
    def __init__(self, settings: Settings):
        self.settings = settings

        self.model = settings.LLM_MODEL_NAME
        self.temperature = settings.LLM_TEMPERATURE

        self.max_retries = 2
        self.timeout = 30
