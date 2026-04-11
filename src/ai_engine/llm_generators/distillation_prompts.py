from typing import List


def get_distillation_prompt(text_chunks: List[str]) -> str:
    """
    Builds a prompt that instructs a language model to distill input text into structured JSON containing key terms, main points, and examples.
    
    The prompt embeds the provided text (joined with two newlines between segments) and requires the model to return only valid JSON with three top-level keys: `key_terms` (list of objects with `term` and `definition`), `main_points` (list of concise strings), and `examples` (list of strings). The prompt also requires preserving the source text language for all JSON values and forbids any surrounding explanatory text.
    
    Parameters:
        text_chunks (List[str]): Segments of the source text to include in the prompt; segments will be joined with two newlines.
    
    Returns:
        str: The assembled prompt string ready to be sent to a language model.
    """
    combined_text = "\n\n".join(text_chunks)

    return f"""Given the following text, identify the most important key terms, main points, and examples.

The goal is to extract structured information that can later be used to generate quiz questions.

Present the output in a structured JSON format with three keys:
- 'key_terms': a list of objects with 'term' and 'definition'
- 'main_points': a list of clear and concise important points
- 'examples': a list of illustrative or practical examples

IMPORTANT: Maintain the language of the source text for all values in the JSON output. Do not translate the content.
Return ONLY valid JSON (no extra text).

Text:
{combined_text}

Example JSON Output:
{{
  "key_terms": [
    {{"term": "Example Term 1", "definition": "Definition of example term 1."}},
    {{"term": "Example Term 2", "definition": "Definition of example term 2."}}
  ],
  "main_points": [
    "Main point 1 of the text.",
    "Main point 2 of the text."
  ],
  "examples": [
    "Example 1 illustrating a concept.",
    "Example 2 explaining a real-world scenario."
  ]
}}
"""
