from transformers import pipeline


summarizer = pipeline(
    "text2text-generation",
    model="google/flan-t5-base"
)


text = "Your long input text here..."


prompt_template = "Summarize the following text concisely:\n{}"
prompt = prompt_template.format(text)


summary = summarizer(
    prompt,
    max_length=150,
    min_length=50
)

print(summary[0]['generated_text'])
