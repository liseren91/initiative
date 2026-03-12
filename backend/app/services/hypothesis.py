from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import selectinload
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.hypothesis import Hypothesis, HypothesisStatus
from app.models.project import Project, ProjectPermission, ProjectPermissionLevel
from app.schemas.hypothesis import HypothesisCreate, HypothesisUpdate
from app.services import task_statuses as task_statuses_service


async def get_all(
    session: AsyncSession,
    guild_id: int,
    *,
    status_filter: Optional[HypothesisStatus] = None,
) -> list[Hypothesis]:
    stmt = (
        select(Hypothesis)
        .where(
            Hypothesis.guild_id == guild_id,
            Hypothesis.deleted_at.is_(None),
        )
        .options(selectinload(Hypothesis.created_by))
        .order_by(Hypothesis.created_at.desc())
    )
    if status_filter is not None:
        stmt = stmt.where(Hypothesis.status == status_filter)
    result = await session.exec(stmt)
    return list(result.all())


async def get_by_id(
    session: AsyncSession,
    hypothesis_id: int,
    guild_id: int,
) -> Hypothesis | None:
    stmt = (
        select(Hypothesis)
        .where(
            Hypothesis.id == hypothesis_id,
            Hypothesis.guild_id == guild_id,
            Hypothesis.deleted_at.is_(None),
        )
        .options(selectinload(Hypothesis.created_by))
    )
    result = await session.exec(stmt)
    return result.one_or_none()


async def create(
    session: AsyncSession,
    data: HypothesisCreate,
    guild_id: int,
    user_id: int,
) -> Hypothesis:
    hypothesis = Hypothesis(
        title=data.title,
        description=data.description,
        status=data.status,
        guild_id=guild_id,
        created_by_id=user_id,
    )
    session.add(hypothesis)
    await session.flush()
    return hypothesis


async def update(
    session: AsyncSession,
    hypothesis_id: int,
    data: HypothesisUpdate,
    guild_id: int,
) -> Hypothesis:
    hypothesis = await get_by_id(session, hypothesis_id, guild_id)
    if hypothesis is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="HYPOTHESIS_NOT_FOUND")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(hypothesis, field, value)
    hypothesis.updated_at = datetime.now(timezone.utc)
    session.add(hypothesis)
    await session.flush()
    return hypothesis


async def soft_delete(
    session: AsyncSession,
    hypothesis_id: int,
    guild_id: int,
) -> Hypothesis:
    hypothesis = await get_by_id(session, hypothesis_id, guild_id)
    if hypothesis is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="HYPOTHESIS_NOT_FOUND")

    now = datetime.now(timezone.utc)
    hypothesis.deleted_at = now
    hypothesis.updated_at = now
    session.add(hypothesis)
    await session.flush()
    return hypothesis


async def promote_to_project(
    session: AsyncSession,
    hypothesis_id: int,
    guild_id: int,
    user_id: int,
    initiative_id: int,
) -> tuple[Hypothesis, Project]:
    hypothesis = await get_by_id(session, hypothesis_id, guild_id)
    if hypothesis is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="HYPOTHESIS_NOT_FOUND")
    if hypothesis.status == HypothesisStatus.project:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="HYPOTHESIS_ALREADY_PROMOTED")
    if hypothesis.project_id is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="HYPOTHESIS_ALREADY_PROMOTED")

    project = Project(
        name=hypothesis.title,
        description=hypothesis.description,
        owner_id=user_id,
        initiative_id=initiative_id,
        guild_id=guild_id,
    )
    session.add(project)
    await session.flush()

    await task_statuses_service.ensure_default_statuses(session, project.id)

    owner_permission = ProjectPermission(
        project_id=project.id,
        user_id=user_id,
        level=ProjectPermissionLevel.owner,
        guild_id=guild_id,
    )
    session.add(owner_permission)

    now = datetime.now(timezone.utc)
    hypothesis.status = HypothesisStatus.project
    hypothesis.project_id = project.id
    hypothesis.updated_at = now
    session.add(hypothesis)
    await session.flush()

    return hypothesis, project
