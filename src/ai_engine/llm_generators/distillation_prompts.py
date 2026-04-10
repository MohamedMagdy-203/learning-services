from typing import List


def get_distillation_prompt(text_chunks: List[str]) -> str:
    """
    Generates a prompt for content distillation to extract key terms and main points.
    The output should be structured and easy to parse.
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
