from openai import AsyncOpenAI
from src.core.config import get_settings

openai_client: AsyncOpenAI | None = None


async def init_openai_client():
    """
    Initialize a single shared OpenAI client instance.
    Runs once at app startup.
    """
    global openai_client
    settings = get_settings()

    openai_client = AsyncOpenAI(
        api_key=settings.GEMINI_API_KEY,
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    )


async def close_openai_client():
    """
    Close OpenAI client on app shutdown.
    """
    global openai_client
    if openai_client:
        await openai_client.close()


def get_openai_client() -> AsyncOpenAI:
    """
    Get initialized OpenAI client.
    """
    if openai_client is None:
        raise RuntimeError("OpenAI client is not initialized")
    return openai_client
