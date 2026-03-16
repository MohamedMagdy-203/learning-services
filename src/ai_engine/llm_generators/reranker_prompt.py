from typing import Any
from src.models.schemas import RoadmapGenerationRequest
from src.ai_engine.llm_generators.source_classifier import classify_source


def build_reranker_prompt(
    requested_data: RoadmapGenerationRequest,
    sources: list[dict[str, Any]],
) -> str:
    profile = requested_data.user_profile_schema
    subtopic = requested_data.target_subtopic_schema
    weaknesses = requested_data.weakness_schema.Topics

    sources_text = ""
    for i, source in enumerate(sources, 1):
        source_type = classify_source(source["url"])
        sources_text += (
            f"[Source {i}] ({source_type.upper()})\n"
            f"Title: {source['title']}\n"
            f"URL: {source['url']}\n"
            f"Content:\n{source['raw_content']}\n"
            f"{'---' * 20}\n"
        )

    weaknesses_text = (
        "\n".join(f"- {topic}: {desc}" for topic, desc in weaknesses.items())
        if weaknesses
        else "- None specified"
    )

    return f"""You are an expert educational content curator. Your job is to analyze learning resources and select the single best resource from each category for a specific learner.

## Learner Profile
- **Tracks:** {", ".join(profile.tracks)}
- **Learning Style:** {profile.learningStyle or "Not specified"}
- **Current Goal:** {profile.currentGoal or "Not specified"}
- **Study Time Per Week:** {profile.studyTimePerWeek or "Not specified"}
- **Role:** {profile.role}

## Target Subtopic
- **Name:** {subtopic.Name}
- **Difficulty:** {subtopic.Difficulty}
- **Description:** {subtopic.Description}

## Known Weaknesses
{weaknesses_text}

## Available Sources
{sources_text}

## Your Task
Analyze all sources above and select:
1. The **best course** (from Coursera, Udemy, or similar platforms) — source_type: "course"
2. The **best YouTube video** — source_type: "video"
3. The **best blog/article** — source_type: "blog"

For each category, pick the most relevant and high-quality source for this specific learner based on their profile, learning style, difficulty level, and weaknesses. If no source exists for a category, set it to null.

Respond ONLY with a valid JSON object. No explanation, no markdown fences, no extra text. Exactly this structure:
{{
  "best_course": {{
    "title": "...",
    "url": "...",
    "reason": "one sentence explaining why this is the best course for this learner"
  }},
  "best_video": {{
    "title": "...",
    "url": "...",
    "reason": "one sentence explaining why this is the best video for this learner"
  }},
  "best_blog": {{
    "title": "...",
    "url": "...",
    "reason": "one sentence explaining why this is the best blog for this learner"
  }}
}}"""
