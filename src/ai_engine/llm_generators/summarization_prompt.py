from typing import List
from langchain_core.documents import Document


def build_summarization_prompt(documents: List[Document]) -> str:
    """
    Builds a simple summarization prompt that:
    Returns structured JSON output
    """

    context_str = "\n\n".join(doc.page_content for doc in documents)
    max_context_chars = 16000
    if len(context_str) > max_context_chars:
        context_str = context_str[:max_context_chars]
    prompt = f"""
You are an AI assistant specialized in summarization.

Your task:
Summarize the following content clearly and concisely.

Important Rules:
1. The summary MUST be in the SAME language as the original content.
2. Do NOT add new information.
3. Keep the meaning accurate.
4. Make the summary clear and well-structured.
5. Keep the summary concise and reasonably sized.

Output format (STRICT JSON ONLY):
{{
  "summary": "your summary here"
}}

Content:
{context_str}
"""

    return prompt
