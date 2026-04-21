from typing import List
from langchain_core.documents import Document


def get_bank_questions_generation_prompt(
    documents: List[Document],
    num_questions: int,
    difficulty_distribution: dict,
) -> str:
    context_str = "\n\n".join(doc.page_content for doc in documents)

    max_context_chars = 16000
    if len(context_str) > max_context_chars:
        context_str = context_str[:max_context_chars]

    return f"""
You are an expert educational quiz generator.
Your task is to generate EXACTLY {num_questions} high-quality multiple-choice questions (MCQs) based ONLY on the provided content.

Content:
{context_str}

RULES:

Output MUST be a valid JSON object with the following structure:
{{
  "questions": [
    {{
      "content": "The question text",
      "options": ["option1", "option2", "option3", "option4"],
      "correct_answer": "The correct option text",
      "explanation": "Why this answer is correct",
      "difficulty": "easy | medium | hard"
    }}
  ]
}}

- You MUST generate EXACTLY {num_questions} questions.
- Do NOT generate any question that is not directly supported by the provided content.
- Do NOT repeat questions.
- Each question must test a different concept.
- Avoid generating questions that are semantically similar.
- Prefer questions that require understanding, not just direct copying from the text.

- You MUST strictly follow this distribution:
   • easy: {difficulty_distribution["easy"]}
   • medium: {difficulty_distribution["medium"]}
   • hard: {difficulty_distribution["hard"]}

IMPORTANT:
- For standard MCQ: provide 4 distinct options.
- correct_answer MUST match one option exactly.

- True/False:
  • English → ["True", "False"]
  • Arabic → ["صحيح", "خطأ"]

- Language MUST match source content.

- Return ONLY the JSON object.

Example:
{{
  "questions": [
    {{
      "content": "Which keyword is used to define a function in Python?",
      "options": ["func", "def", "function", "define"],
      "correct_answer": "def",
      "explanation": "In Python, the 'def' keyword is used.",
      "difficulty": "easy"
    }}
  ]
}}
"""
