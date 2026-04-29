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
    Topics: Optional[Dict[str, str]]


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
    urls: List[HttpUrl] = Field(default_factory=list)
    subtopic_name: Optional[str] = None
    subtopic_difficulty: Optional[str] = "Intermediate"
    primary_url: Optional[HttpUrl] = None
    weaknesses: Optional[Dict[str, str]] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_primary_url_membership(self) -> "MindmapGenerationRequest":
        if self.primary_url is None:
            return self

        if self.primary_url not in self.urls:
            raise ValueError(
                f"primary_url '{self.primary_url}' must be one of the provided urls"
            )
        return self


class MindmapNodeSchema(BaseModel):
    topic: str
    description: str
    children: list["MindmapNodeSchema"] = Field(default_factory=list)


MindmapNodeSchema.model_rebuild()


class MindmapResponseSchema(BaseModel):
    user_id: str
    subtopic_id: str
    mindmap: MindmapNodeSchema
