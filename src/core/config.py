from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")
    APP_NAME: str = "Learning Services"
    APP_VERSION: str = "1.0.0"
    MAIN_BACKEND_URL: str = "http://localhost:3000"
    TAVILY_API_KEY: str = "tvly-..."


@lru_cache
def get_settings():
    return Settings()
