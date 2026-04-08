import pytest
import json
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient
from src.main import app
from src.models.distillation_schemas import ContentDistillationResponse


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c

# Mock Data for Testing
MOCK_URL = "https://example.com/python-basics"
MOCK_CHUNKS = ["Python is a high-level language.", "It is used for data science."]
MOCK_LLM_RESPONSE = {
    "key_terms": [
        {"term": "Python", "definition": "A high-level programming language."}
    ],
    "main_points": ["Python is versatile", "Great for beginners"],
    "examples": ["Web development with Django"]
}


@patch("src.ai_engine.distiller_engine.distiller.retrieve_chunks_by_url")
@patch("src.ai_engine.distiller_engine.distiller.OpenAI")
def test_distill_content_route_success(mock_openai_class, mock_retrieve_chunks, client):
    """
    This test ensures the full pipeline works:
    1. Calls Retrieval and gets Chunks.
    2. Sends Chunks to LLM and receives JSON.
    3. Returns the Response correctly formatted according to the Schema.
    """
   
    mock_retrieve_chunks.return_value = MOCK_CHUNKS
    
    
    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(message=MagicMock(content=json.dumps(MOCK_LLM_RESPONSE)))
    ]
    
    mock_client_instance = mock_openai_class.return_value
    mock_client_instance.chat.completions.create.return_value = mock_response

  
    response = client.post(
        "/api/v1/dist/distill-content",
        json={"url": MOCK_URL}
    )


    assert response.status_code == 200
    data = response.json()
    assert data["url"] == MOCK_URL
    assert "distilled_content" in data
    assert len(data["distilled_content"]["key_terms"]) > 0
    assert data["distilled_content"]["key_terms"][0]["term"] == "Python"


@patch("src.ai_engine.distiller_engine.distiller.retrieve_chunks_by_url")
def test_distill_content_no_chunks(mock_retrieve_chunks, client):
    """
    Ensures the system returns an error (400 or 404) if no chunks are found for the URL.
    """

    mock_retrieve_chunks.return_value = []

    response = client.post(
        "/api/v1/dist/distill-content",
        json={"url": "https://unknown-url.com"}
    )


    assert response.status_code in [400, 404]


@patch("src.ai_engine.data_fetchers.distillation_retrieval.QdrantClient")
@patch("src.ai_engine.data_fetchers.distillation_retrieval.get_settings")
def test_retrieve_chunks_by_url_logic(mock_get_settings, mock_qdrant_class):
    """
    Tests the logic of retrieving chunks from Qdrant independently.
    """
    from src.ai_engine.data_fetchers.distillation_retrieval import retrieve_chunks_by_url
    

    mock_client_instance = mock_qdrant_class.return_value
    mock_get_settings.return_value.QDRANT_COLLECTION_NAME = "test_collection"
    
    
    mock_point = MagicMock()
    mock_point.payload = {"page_content": "Test content from Qdrant", "metadata": {"url": MOCK_URL}}
    mock_client_instance.scroll.return_value = ([mock_point], None)


    chunks = retrieve_chunks_by_url(MOCK_URL)

    
    assert len(chunks) == 1
    assert chunks[0] == "Test content from Qdrant"
    mock_client_instance.scroll.assert_called_once()


    #python -m pytest tests/test_distillation.py

