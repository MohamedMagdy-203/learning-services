from src.models.schemas import MindmapGenerationRequest

def build_mindmap_prompt(
    request: MindmapGenerationRequest,
    chunks: list[str],
) -> str:
    """
    Build a structured prompt for Gemini to generate a mind map.

    Uses only the fields that genuinely affect mindmap structure:
    - subtopic_name        → root node title + scope
    - subtopic_difficulty  → depth and complexity of branches
    - weaknesses           → which areas to prioritise
    - chunks               → actual content to organise

    

    Args:
        request: the full mindmap generation request.
        chunks:  combined content chunks from all available sources.

    Returns:
        A fully constructed prompt string ready to send to the LLM.
    """
    weaknesses_text = (
        "\n".join(
            f"- {topic}: {desc}" for topic, desc in request.weaknesses.items()
        )
        if request.weaknesses
        else "- None specified"
    )

    chunks_text = "\n\n".join(
        f"[Chunk {i}]\n{chunk}" for i, chunk in enumerate(chunks, 1)
    )

    return f"""You are an expert educational content structurer. \
Your job is to analyse learning content and organise it into a clear, \
hierarchical mind map.

## Target Subtopic
- **Name:** {request.subtopic_name}
- **Difficulty:** {request.subtopic_difficulty}


## Learner's Known Weaknesses
{weaknesses_text}

## Learning Content
{chunks_text}

## Your Task
Analyse the learning content above and organise it into a hierarchical mind map. \
Follow these rules strictly:

1. The root node topic must be exactly: "{request.subtopic_name}"
2. Create 4 to 6 main branches covering the core concepts found in the content.
3. Each main branch must have 2 to 4 sub-topics.
4. Prioritise branches and sub-topics that address the learner's known weaknesses.
5. Match depth and complexity to the "{request.subtopic_difficulty}" difficulty level.
6. Use clear, concise topic names — no full sentences.
7. Base ONLY on the provided content — do not invent topics not covered in the chunks.

Respond ONLY with a valid JSON object. \
No explanation, no markdown fences, no extra text. Exactly this structure:
{{
  "topic": "{request.subtopic_name}",
  "children": [
    {{
      "topic": "Main concept 1",
      "children": [
        {{ "topic": "Sub-topic 1.1", "children": [] }},
        {{ "topic": "Sub-topic 1.2", "children": [] }}
      ]
    }},
    {{
      "topic": "Main concept 2",
      "children": [
        {{ "topic": "Sub-topic 2.1", "children": [] }},
        {{ "topic": "Sub-topic 2.2", "children": [] }}
      ]
    }}
  ]
}}"""