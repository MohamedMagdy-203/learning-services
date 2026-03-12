from pydantic import BaseModel
from typing import List, Dict, Optional


class UserProfileSchema(BaseModel):
    id: str
    tracks: List[str]
    learningStyle: Optional[str] = None
    currentGoal: Optional[str] = None
    studyTimePerWeek: Optional[str] = None
    role: str


class TargetSubtopicSchema(BaseModel):
    Name: str
    Description: str
    Difficulty: str


class WeaknessSchema(BaseModel):
    Topics: Dict[str, str]


class RoadmapGenerationRequest(BaseModel):
    user_profile_schema: UserProfileSchema
    target_subtopic_schema: TargetSubtopicSchema
    weakness_schema: WeaknessSchema
