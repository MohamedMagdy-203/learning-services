from src.models.schemas import RoadmapGenerationRequest


def query_builder(requested_data: RoadmapGenerationRequest) -> str:
    subtopic_name = requested_data.target_subtopic_schema.Name
    subtopic_difficulty = requested_data.target_subtopic_schema.Difficulty

    search_query = (
        f"{subtopic_name} {subtopic_difficulty} level " f"tutorial guide course "
    )
    return search_query
