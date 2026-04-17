from pydantic import BaseModel
from typing import List, Dict, Optional
from pydantic import ConfigDict, HttpUrl, Field, model_validator
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
    urls: List[HttpUrl] = Field(min_length=1)
    primary_url: HttpUrl
    subtopic_name: str
    subtopic_difficulty: str
    weaknesses: Optional[Dict[str, str]] = None

    @model_validator(mode="after")
    def validate_primary_url_membership(self) -> "MindmapGenerationRequest":
        if self.primary_url not in self.urls:
            raise ValueError("primary_url must be one of urls")
        return self


class MindmapNodeSchema(BaseModel):
    topic: str
    children: list["MindmapNodeSchema"] = Field(default_factory=list)


MindmapNodeSchema.model_rebuild()


class MindmapResponseSchema(BaseModel):
    user_id: str
    subtopic_id: str
    mindmap: MindmapNodeSchema
