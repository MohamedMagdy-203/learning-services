from qdrant_client import QdrantClient
from src.core.config import get_settings
from sentence_transformers import SentenceTransformer
from functools import lru_cache
from transformers import pipeline


settings = get_settings()
client = QdrantClient(url=settings.QDRANT_URL)
collection_name = settings.QDRANT_COLLECTION_NAME


embed_model = SentenceTransformer("paraphrase-multilingual-mpnet-base-v2")


def fetch_context_from_qdrant(query_text: str, top_k: int = 3) -> str:
    query_vector = embed_model.encode(query_text).tolist()

    results = client.search(
        collection_name=collection_name,
        query_vector=query_vector,
        limit=top_k
    )

    context_texts = [
        r.payload["page_content"] for r in results if "page_content" in r.payload
    ]

    return "\n\n".join(context_texts)



@lru_cache(maxsize=1)
def get_summarizer():
    return pipeline(
        "text2text-generation",
        model="google/flan-t5-base"
    )

# Prompt template with detailed instructions for learning content
prompt_template = """
You are an expert instructor. Summarize the following content in a way that is clear and easy for learners.
Your summary should:
- Highlight all key concepts and technical terms related to the topic "{title}"
- Provide concise explanations suitable for beginners
- Include examples or practical insights if relevant
- Keep it structured and easy to read (bullet points or short paragraphs)
- Mention the source title and type at the end

Content:
{context_texts}
"""

def summarize_text(context_texts: str, title: str, max_length: int = 350, min_length: int = 50) -> str:
    """
    Summarize the page content with context from the title.
    """
    summarizer = get_summarizer()
    prompt = prompt_template.format(context_texts, title=title)
    summary = summarizer(prompt, max_length=max_length, min_length=min_length)
    return summary[0]["generated_text"]