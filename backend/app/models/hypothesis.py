from datetime import datetime, timezone
from enum import Enum
from typing import Optional, TYPE_CHECKING

from sqlalchemy import Column, DateTime, String
from sqlmodel import Enum as SQLEnum, Field, Relationship, SQLModel

if TYPE_CHECKING:  # pragma: no cover
    from app.models.project import Project
    from app.models.user import User
    from app.models.guild import Guild


class HypothesisStatus(str, Enum):
    idea = "idea"
    evaluation = "evaluation"
    research = "research"
    decision = "decision"
    project = "project"
    rejected = "rejected"
    paused = "paused"


class Hypothesis(SQLModel, table=True):
    __tablename__ = "hypotheses"

    id: Optional[int] = Field(default=None, primary_key=True)
    guild_id: Optional[int] = Field(default=None, foreign_key="guilds.id", nullable=True)
    project_id: Optional[int] = Field(default=None, foreign_key="projects.id", nullable=True)
    title: str = Field(nullable=False)
    description: Optional[str] = Field(default=None)
    status: HypothesisStatus = Field(
        default=HypothesisStatus.idea,
        sa_column=Column(
            SQLEnum(HypothesisStatus, name="hypothesis_status"),
            nullable=False,
        ),
    )
    created_by_id: Optional[int] = Field(default=None, foreign_key="users.id", nullable=True)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    deleted_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
    )

    created_by: Optional["User"] = Relationship()
    project: Optional["Project"] = Relationship()
    guild: Optional["Guild"] = Relationship()
