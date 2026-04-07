from transformers import pipeline


summarizer = pipeline(
    "text2text-generation",
    model="google/flan-t5-base"
)


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

# Format the prompt with the content title and page content
prompt = prompt_template.format(page_content, title=metadata['title'])


summary = summarizer(
    prompt,
    max_length=150,
    min_length=50
)

print(summary[0]['generated_text'])
