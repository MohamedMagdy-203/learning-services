from src.models.schemas import MindmapGenerationRequest
import json


def build_mindmap_prompt(
    request: MindmapGenerationRequest,
    chunks: list[str],
) -> str:
    """
    Build a structured prompt for Gemini to generate a mind map.

    Uses only the fields that genuinely affect mindmap structure:
    - subtopic_name        → root node title + scope
    - subtopic_difficulty  → depth and complexity of branches
    - weaknesses           → which areas to prioritize
    - chunks               → actual content to organize

    Args:
        request: the full mindmap generation request.
        chunks:  combined content chunks from all available sources.

    Returns:
        A fully constructed prompt string ready to send to the LLM.
    """
    weaknesses_text = (
        "\n".join(f"- {topic}: {desc}" for topic, desc in request.weaknesses.items())
        if request.weaknesses
        else "- None specified"
    )

    chunks_text = "\n\n".join(
        f"[Chunk {i}]\n{chunk}" for i, chunk in enumerate(chunks, 1)
    )
    subtopic_name_json = json.dumps(request.subtopic_name)

    return f"""You are an expert in educational content structuring. \
Your job is to analyze learning content and organize it into a clear, \
hierarchical mind map.

## Target Subtopic
- **Name:** {request.subtopic_name}
- **Difficulty:** {request.subtopic_difficulty}

## Learner's Known Weaknesses
{weaknesses_text}

## Learning Content
{chunks_text}

## Your Task
Analyze the learning content above and organize it into a hierarchical mind map. \
Follow these rules strictly:

1. The root node topic must be exactly: {subtopic_name_json}
2. **STRICT GENERALIZATION (Vendor-Neutral):** The target subtopic is "{request.subtopic_name}". Since this is a general fundamental topic, you MUST REMOVE all vendor-specific jargon. For example, replace "PL/SQL" or "T-SQL" with "Procedural SQL", and ignore specific software names (e.g., Oracle, SQL Server, MySQL). Map everything to standard ANSI SQL concepts.
3. **STRICT SIZE & DEPTH LIMITS (CRITICAL FOR SPEED):**
   - Maximum 2 levels of depth (Root -> Main Branch -> Sub-topic).
   - Maximum 4 to 5 Main Branches.
   - Maximum 4 Sub-topics per Main Branch.
   - DO NOT over-expand. Keep the map highly focused.
4. **Descriptions:** Write a 1-sentence "description" for the Root and Main Branches. For the final Sub-topics, leave the description completely empty ("").
5. Prioritize branches addressing the learner's weaknesses.

Respond ONLY with a valid JSON object matching this structure:
{{
  "topic": {subtopic_name_json},
  "description": "Short explanation",
  "children": [
    {{
      "topic": "Main Branch 1",
      "description": "Short explanation",
      "children": [
        {{
          "topic": "Sub-topic 1.1",
          "description": "",
          "children": []
        }}
      ]
    }}
  ]
}}"""
