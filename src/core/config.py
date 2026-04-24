from pydantic_settings import BaseSettings, SettingsConfigDict  # type: ignore
from functools import lru_cache


class Settings(BaseSettings):  # type: ignore
    model_config = SettingsConfigDict(env_file=".env")  # type: ignore
    APP_NAME: str = "Learning Services"
    APP_VERSION: str = "1.0.0"
    MAIN_BACKEND_URL: str = "http://localhost:3000"
    TAVILY_API_KEY: str
    GEMINI_API_KEY: str
    LLM_MODEL_NAME: str = "gemini-2.5-flash-lite"
    LLM_TEMPERATURE: float = 0.3
    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_COLLECTION_NAME: str = "learning_materials"
    QUIZ_COLLECTION_NAME: str = "quiz_questions"
    GEMINI_RERANKER_TIMEOUT_MS: int = 60000
    HF_TOKEN: str
    RERANKER_MODEL: str = "gemini-2.5-flash-lite"
    MINDMAP_MODEL: str = "gemini-2.5-flash-lite"
    PRIMARY_URL_CHUNKS_LIMIT: int = 15
    SECONDARY_URL_CHUNKS_LIMIT: int = 5
    EMBEDDING_MODEL: str = "paraphrase-multilingual-mpnet-base-v2"


@lru_cache
def get_settings():
    return Settings()  # type: ignore
