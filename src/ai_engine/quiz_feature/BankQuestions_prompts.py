from typing import List
from langchain_core.documents import Document


def get_bank_questions_generation_prompt(
    documents: List[Document],
    num_questions: int,
    difficulty_distribution: dict,
) -> str:
    context_str = "\n\n".join(doc.page_content for doc in documents)

    return f"""
You are a STRICT quiz generation engine.

You MUST generate EXACTLY {num_questions} VALID and UNIQUE multiple-choice questions.
Failure to meet ANY requirement means your response is invalid.

<source_content>
{context_str}
</source_content>

========================
CRITICAL RULES (NO EXCEPTIONS)
========================

1. You MUST return EXACTLY {num_questions} questions.
2. Each question MUST:
   - Have non-empty "content"
   - Have valid options (at least 2)
   - Have a correct_answer that EXACTLY matches one option
   - Be directly supported by the source content
3. NO duplicate or semantically similar questions.
4. If unsure → generate a DIFFERENT valid question instead of skipping.
5. DO NOT reduce the number of questions under any condition.

========================
DIFFICULTY DISTRIBUTION (STRICT)
========================
- easy: {difficulty_distribution["easy"]}
- medium: {difficulty_distribution["medium"]}
- hard: {difficulty_distribution["hard"]}

========================
OUTPUT FORMAT (STRICT JSON)
========================
Return ONLY a valid JSON object:

{{
  "questions": [
    {{
      "content": "The question text",
      "options": ["option1", "option2", "option3", "option4"],
      "correct_answer": "The correct option text",

      "explanations": {{
        "option1": "Why this option is correct or incorrect",
        "option2": "Why this option is correct or incorrect",
        "option3": "Why this option is correct or incorrect",
        "option4": "Why this option is correct or incorrect"
      }},

      "difficulty": "easy | medium | hard"
    }}
  ]
}}

========================
IMPORTANT DETAILS
========================

- For standard MCQ: provide 4 distinct options.
- Each option MUST have a corresponding explanation.
- correct_answer MUST match one option exactly.
- Do NOT return empty fields.
- Language MUST match source content IF arabic answer in arabic and if english answer in english.

- For True/False MCQ:
  • English → ["True", "False"]
  • Arabic → ["صحيح", "خطأ"]

========================
EXAMPLE (FOLLOW THIS FORMAT EXACTLY)
========================

{{
  "questions": [
    {{
      "content": "Which keyword is used to define a function in Python?",
      "options": ["func", "def", "function", "define"],
      "correct_answer": "def",

      "explanations": {{
        "func": "Incorrect because Python does not use 'func' keyword.",
        "def": "Correct because 'def' is used to define functions in Python.",
        "function": "Incorrect because it's not a valid Python keyword.",
        "define": "Incorrect because Python does not use 'define' keyword."
      }},

      "difficulty": "easy"
    }}
  ]
}}

========================
SELF-CHECK BEFORE RETURNING
========================

- Count questions → MUST be {num_questions}
- Ensure NO duplicates
- Ensure ALL questions valid
- Ensure correct difficulty distribution
- Ensure correct_answer matches options EXACTLY
- Ensure each option has explanation

If ANY rule is violated → FIX it before returning.

DO NOT explain.
RETURN JSON ONLY.
"""
