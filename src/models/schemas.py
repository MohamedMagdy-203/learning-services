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

class MindmapGenerationRequest(BaseModel):
    user_id: str
    subtopic_id: str

    # Source URLs — any can be None if not available
    best_course_url: Optional[str] = None
    best_video_url: Optional[str] = None
    best_blog_url: Optional[str] = None

    # Subtopic context needed for the prompt 
    subtopic_name: str
    subtopic_difficulty: str

    # Learner weaknesses — used to personalise the mindmap
    weaknesses: Dict[str, str]

class MindmapNodeSchema(BaseModel):
    topic: str
    children: list["MindmapNodeSchema"] = []


MindmapNodeSchema.model_rebuild()


class MindmapResponseSchema(BaseModel):
    user_id: str
    subtopic_id: str
    mindmap: MindmapNodeSchema
     