from src.models.schemas import RoadmapGenerationRequest


def query_builder(requested_data: RoadmapGenerationRequest) -> str:
    tracks = requested_data.user_profile_schema.tracks
    track_name = tracks[0] if tracks else "General"

    subtopic_name = requested_data.target_subtopic_schema.Name
    subtopic_difficulty = requested_data.target_subtopic_schema.Difficulty

    search_query = (
        f"{subtopic_name} {subtopic_difficulty} level "
        f"tutorial guide course "
        f"for {track_name} developers"
    )
    return search_query
