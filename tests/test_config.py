import pytest
from src.core.config import Settings


def test_settings_default_values():
    settings = Settings(TAVILY_API_KEY="test_key", GEMINI_API_KEY="test_key")
    assert settings.APP_NAME == "Learning Services"
    assert settings.APP_VERSION == "1.0.0"


def test_settings_env_override(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MAIN_BACKEND_URL", "http://fake-server:9999")
    settings = Settings(TAVILY_API_KEY="test_key", GEMINI_API_KEY="test_key")
    assert settings.MAIN_BACKEND_URL == "http://fake-server:9999"
