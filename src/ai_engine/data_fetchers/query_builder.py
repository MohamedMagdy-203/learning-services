from src.models.schemas import RoadmapGenerationRequest


def query_builder(requested_data: RoadmapGenerationRequest) -> str:
    # User Info
    tracks = requested_data.user_profile_schema.tracks
    track_name = tracks[0] if tracks else "General"

    # Subtopic Info
    subtopic_name = requested_data.target_subtopic_schema.Name
    subtopic_description = requested_data.target_subtopic_schema.Description
    subtopic_difficulty = requested_data.target_subtopic_schema.Difficulty

    search_query = (
        f"{subtopic_name} {subtopic_description} "
        f"{subtopic_difficulty} level "
        f"guide tutorial explanation documentation papers examples"
        f"{track_name} "
    )
    return search_query
