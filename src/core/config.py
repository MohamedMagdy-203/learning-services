from pydantic_settings import BaseSettings, SettingsConfigDict  # type: ignore
from functools import lru_cache


class Settings(BaseSettings):  # type: ignore
    model_config = SettingsConfigDict(env_file=".env")  # type: ignore
    APP_NAME: str = "Learning Services"
    APP_VERSION: str = "1.0.0"
    MAIN_BACKEND_URL: str = "http://localhost:3000"
    TAVILY_API_KEY: str
    GEMINI_API_KEY: str
    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_COLLECTION_NAME: str = "learning_materials"
    GEMINI_RERANKER_TIMEOUT_MS: int = 60000
    hf_token: str | None = None


@lru_cache
def get_settings():
    return Settings()  # type: ignore
