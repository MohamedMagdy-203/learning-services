from pydantic import BaseModel
from typing import List, Dict, Optional
from pydantic import ConfigDict
from pydantic.alias_generators import to_camel


class UserProfileSchema(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)
    id: str
    tracks: List[str]
    learningStyle: Optional[str] = None
    currentGoal: Optional[str] = None
    studyTimePerWeek: Optional[str] = None
    role: str


class TargetSubtopicSchema(BaseModel):
    Subtopic_id: str
    Name: str
    Description: str
    Difficulty: str


class WeaknessSchema(BaseModel):
    Topics: Dict[str, str]


class RoadmapGenerationRequest(BaseModel):
    user_profile_schema: UserProfileSchema
    target_subtopic_schema: TargetSubtopicSchema
    weakness_schema: WeaknessSchema


class RankedSourceSchema(BaseModel):
    model_config = ConfigDict(extra="ignore")
    title: str
    url: str


class RoadmapRankedResultSchema(BaseModel):
    user_id: str
    subtopic_id: str
    best_course: RankedSourceSchema | None
    best_video: RankedSourceSchema | None
    best_blog: RankedSourceSchema | None


class SummarizationRequest(BaseModel):
    page_content: str
    title: str
    max_length: int = 350
    min_length: int = 50