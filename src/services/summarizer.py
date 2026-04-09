from functools import lru_cache
from transformers import pipeline


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
{}
"""

def summarize_text(page_content: str, title: str, max_length: int = 350, min_length: int = 50) -> str:
    """
    Summarize the page content with context from the title.
    """
    summarizer = get_summarizer()
    prompt = prompt_template.format(page_content, title=title)
    summary = summarizer(prompt, max_length=max_length, min_length=min_length)
    return summary[0]["generated_text"]