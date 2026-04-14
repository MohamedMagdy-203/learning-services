from typing import Dict


def get_bank_questions_generation_prompt(
    distilled_content: Dict, num_questions: int, difficulty: str
) -> str:
    """
    Generates a prompt for the LLM to create questions based on distilled content.
    All questions will be in Multiple Choice Question (MCQ) format.
    The output must strictly follow the schema provided in the prompt.
    Language of the questions must match the language of the source content.
    """
    content_str = str(distilled_content)

    return f"""
Based on the following content, generate {num_questions} questions with a \'{difficulty}\' difficulty level.
All questions MUST be in Multiple-Choice (MCQ) format.


Content:
{content_str}

Output MUST be a JSON array of objects. Each object must strictly follow this structure:
- content: "The question text"
- options: ["option1", "option2", "option3", "option4"] (For True/False questions, this MUST be ["True", "False"])
- correct_answer: "The correct option text ( one of the options, or \'True\' / \'False\' for T/F questions)"
- explanation: "Why this answer is correct"
- difficulty: "{difficulty}"

IMPORTANT:
- For standard MCQ: provide 4 distinct options in the \'options\' list.
- For True/False questions: the \'options\' list MUST contain exactly ["True", "False"].
-The questions, options, and explanations MUST be written in the SAME LANGUAGE as the source content provided below.
If the content is in Arabic, generate everything in Arabic.
If the content is in English, generate everything in English.
- Return ONLY the JSON array.

Here are concise examples of the expected JSON output format:

Example 1
{{
    "content": "Which keyword is used to define a function in Python?",
    "options": ["func", "def", "function", "define"],
    "correct_answer": "def",
    "explanation": "In Python, the 'def' keyword is used to define a function.",
    "difficulty": "easy"
}}

Example 2
{{
    "content": "تعتبر JavaScript لغة برمجة من جانب الخادم (Server-side).",
    "options": ["صحيح", "خطأ"],
    "correct_answer": "خطأ",
    "explanation": "JavaScript تستخدم بشكل أساسي كلغة برمجة من جانب العميل (Client-side) في المتصفحات، ولكن يمكن استخدامها من جانب الخادم أيضاً مع Node.js.",
    "difficulty": "medium"
}} """
