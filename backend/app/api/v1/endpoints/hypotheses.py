from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import selectinload

from app.api.deps import (
    RLSSessionDep,
    get_current_active_user,
    get_guild_membership,
    GuildContext,
)
from app.db.session import reapply_rls_context
from app.models.hypothesis import Hypothesis, HypothesisStatus
from app.models.user import User
from app.schemas.hypothesis import (
    HypothesisCreate,
    HypothesisPromoteResponse,
    HypothesisResponse,
    HypothesisUpdate,
)
from app.schemas.project import ProjectRead
from app.services import hypothesis as hypothesis_service

router = APIRouter()
GuildContextDep = Annotated[GuildContext, Depends(get_guild_membership)]


@router.get("/", response_model=List[HypothesisResponse])
async def list_hypotheses(
    session: RLSSessionDep,
    current_user: Annotated[User, Depends(get_current_active_user)],
    guild_context: GuildContextDep,
    status_filter: Optional[HypothesisStatus] = Query(default=None, alias="status"),
) -> List[Hypothesis]:
    return await hypothesis_service.get_all(
        session,
        guild_context.guild_id,
        status_filter=status_filter,
    )


@router.get("/{hypothesis_id}", response_model=HypothesisResponse)
async def read_hypothesis(
    hypothesis_id: int,
    session: RLSSessionDep,
    current_user: Annotated[User, Depends(get_current_active_user)],
    guild_context: GuildContextDep,
) -> Hypothesis:
    hypothesis = await hypothesis_service.get_by_id(
        session, hypothesis_id, guild_context.guild_id,
    )
    if hypothesis is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="HYPOTHESIS_NOT_FOUND")
    return hypothesis


@router.post("/", response_model=HypothesisResponse, status_code=status.HTTP_201_CREATED)
async def create_hypothesis(
    data: HypothesisCreate,
    session: RLSSessionDep,
    current_user: Annotated[User, Depends(get_current_active_user)],
    guild_context: GuildContextDep,
) -> Hypothesis:
    hypothesis = await hypothesis_service.create(
        session,
        data,
        guild_id=guild_context.guild_id,
        user_id=current_user.id,
    )
    await session.commit()
    await reapply_rls_context(session)
    refreshed = await hypothesis_service.get_by_id(
        session, hypothesis.id, guild_context.guild_id,
    )
    return refreshed


@router.patch("/{hypothesis_id}", response_model=HypothesisResponse)
async def update_hypothesis(
    hypothesis_id: int,
    data: HypothesisUpdate,
    session: RLSSessionDep,
    current_user: Annotated[User, Depends(get_current_active_user)],
    guild_context: GuildContextDep,
) -> Hypothesis:
    hypothesis = await hypothesis_service.update(
        session,
        hypothesis_id,
        data,
        guild_id=guild_context.guild_id,
    )
    await session.commit()
    await reapply_rls_context(session)
    refreshed = await hypothesis_service.get_by_id(
        session, hypothesis.id, guild_context.guild_id,
    )
    return refreshed


@router.delete("/{hypothesis_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_hypothesis(
    hypothesis_id: int,
    session: RLSSessionDep,
    current_user: Annotated[User, Depends(get_current_active_user)],
    guild_context: GuildContextDep,
) -> None:
    await hypothesis_service.soft_delete(
        session,
        hypothesis_id,
        guild_id=guild_context.guild_id,
    )
    await session.commit()


@router.post("/{hypothesis_id}/promote", response_model=HypothesisPromoteResponse)
async def promote_hypothesis(
    hypothesis_id: int,
    session: RLSSessionDep,
    current_user: Annotated[User, Depends(get_current_active_user)],
    guild_context: GuildContextDep,
    initiative_id: int = Query(..., description="Initiative to create the project in"),
) -> dict:
    hypothesis, project = await hypothesis_service.promote_to_project(
        session,
        hypothesis_id,
        guild_id=guild_context.guild_id,
        user_id=current_user.id,
        initiative_id=initiative_id,
    )
    await session.commit()
    await reapply_rls_context(session)

    refreshed_hypothesis = await hypothesis_service.get_by_id(
        session, hypothesis.id, guild_context.guild_id,
    )

    from sqlmodel import select
    from app.models.project import Project
    result = await session.exec(
        select(Project).where(Project.id == project.id)
        .options(selectinload(Project.owner))
    )
    refreshed_project = result.one()

    return {
        "hypothesis": refreshed_hypothesis,
        "project": ProjectRead.model_validate(refreshed_project),
    }
