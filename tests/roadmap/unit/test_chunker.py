import pytest  # type: ignore
import logging
from src.ai_engine.text_processing.chunker import chunk_text
from src.core.mock_data import MOCK_CLEANED_RESPONSE, arabic_content

logging.basicConfig(level=logging.INFO)


@pytest.mark.integration  # type: ignore
@pytest.mark.asyncio  # type: ignore
async def test_chunk_text_english():
    raw_content = MOCK_CLEANED_RESPONSE[0]["raw_content"]

    chunks = chunk_text(raw_content)

    assert len(chunks) > 0
    assert all(isinstance(chunk, str) for chunk in chunks)
    assert all(len(chunk) > 0 for chunk in chunks)

    print("\n\n" + "=" * 50)
    print("CHUNKING RESULTS — ENGLISH")
    print("=" * 50)
    print(f"Input length  : {len(raw_content)} chars")
    print(f"Chunks produced: {len(chunks)}")
    for i, chunk in enumerate(chunks, 1):
        print(f"\n--- [ Chunk {i} ] ---")
        print(f"Length: {len(chunk)} chars")
        print(f"Preview: {chunk[:200]}")
    print("=" * 50 + "\n")


@pytest.mark.integration  # type: ignore
@pytest.mark.asyncio  # type: ignore
async def test_chunk_text_arabic():
    chunks = chunk_text(arabic_content)

    assert len(chunks) > 0

    print("\n\n" + "=" * 50)
    print("CHUNKING RESULTS — ARABIC")
    print("=" * 50)
    print(f"Input length  : {len(arabic_content)} chars")
    print(f"Chunks produced: {len(chunks)}")
    for i, chunk in enumerate(chunks, 1):
        print(f"\n--- [ Chunk {i} ] ---")
        print(f"Length: {len(chunk)} chars")
        print(f"Preview: {chunk[:200]}")
    print("=" * 50 + "\n")
