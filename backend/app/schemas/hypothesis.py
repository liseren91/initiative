from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.models.hypothesis import HypothesisStatus
from app.schemas.project import ProjectRead
from app.schemas.user import UserPublic


class HypothesisCreate(BaseModel):
    title: str
    description: Optional[str] = None
    status: HypothesisStatus = HypothesisStatus.idea


class HypothesisUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[HypothesisStatus] = None


class HypothesisResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, json_schema_serialization_defaults_required=True)

    id: int
    guild_id: Optional[int] = None
    project_id: Optional[int] = None
    title: str
    description: Optional[str] = None
    status: HypothesisStatus
    created_by_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None
    created_by: Optional[UserPublic] = None


class HypothesisPromoteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, json_schema_serialization_defaults_required=True)

    hypothesis: HypothesisResponse
    project: ProjectRead
