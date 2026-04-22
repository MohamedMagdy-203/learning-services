from typing import List, Dict
from langchain_core.documents import Document


def build_summarization_prompt(
    documents: List[Document],
    subtopic_name: str,
    subtopic_difficulty: str,
    weaknesses: Dict[str, str],
) -> str:
    """
    Builds a personalized summarization prompt.
    """
    if not documents:
        raise ValueError("Cannot build prompt: no documents provided")

    context_str = "\n\n".join(doc.page_content for doc in documents)

    weaknesses_str = "None"
    if weaknesses:
        weaknesses_str = "\n".join([f"- {k}: {v}" for k, v in weaknesses.items()])

    prompt = f"""
You are an expert AI tutor specialized in summarizing educational content.

Content Context:
- Topic: {subtopic_name}
- Target Audience Difficulty: {subtopic_difficulty}
- User's Specific Weaknesses:
{weaknesses_str}

Your task:
Summarize the provided content comprehensively, tailoring the explanation to address the user's weaknesses and matching the specified difficulty level.

Important Rules:
1. The summary MUST be in the SAME language as the original content.
2. Pay special attention to the user's weaknesses. Explain these specific areas very clearly and provide extra context if needed based on the text.
3. Structure the summary beautifully using Markdown formatting:
   - Use a main Heading 1 (#) for the overall topic.
   - Use Heading 2 (##) for subtopics/sections.
   - Use bullet points under each section for readability.
   - Bold important terms.
4. Do NOT add fabricated information outside the provided content.

Output format (STRICT JSON ONLY):
{{
  "summary": "Your fully Markdown-formatted summary string goes here (ensure to properly escape newlines as \\n within the JSON string)"
}}

Content:
{context_str}
"""
    return prompt
