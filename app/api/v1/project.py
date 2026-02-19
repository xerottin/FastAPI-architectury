from typing import Optional
from uuid import UUID

from auth.dependencies import get_current_user
from services.project import create_project, delete_project, get_project, list_projects, my_project, update_project
from db.session import get_pg_db
from fastapi import APIRouter, Depends, status
from models import User
from schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project_endpoint(
    payload: ProjectCreate,
    db: AsyncSession = Depends(get_pg_db),
    current_user: User = Depends(get_current_user),
):
    return await create_project(payload, db, current_user)


@router.get("/list", response_model=list[ProjectResponse], status_code=status.HTTP_200_OK)
async def list_projects_endpoint(
    db: AsyncSession = Depends(get_pg_db),
    current_user: User = Depends(get_current_user),
):
    return await list_projects(db, current_user)


@router.get("/my", response_model=Optional[ProjectResponse], status_code=status.HTTP_200_OK)
async def my_project_endpoint(
    db: AsyncSession = Depends(get_pg_db),
    current_user: User = Depends(get_current_user),
):
    return await my_project(db, current_user)


@router.get("/{public_id}", response_model=ProjectResponse, status_code=status.HTTP_200_OK)
async def get_project_endpoint(
    public_id: UUID,
    db: AsyncSession = Depends(get_pg_db),
    current_user: User = Depends(get_current_user),
):
    return await get_project(public_id, db, current_user)


@router.patch("/{public_id}", response_model=ProjectResponse, status_code=status.HTTP_200_OK)
async def update_project_endpoint(
    public_id: UUID,
    payload: ProjectUpdate,
    db: AsyncSession = Depends(get_pg_db),
    current_user: User = Depends(get_current_user),
):
    return await update_project(public_id, payload, db, current_user)


@router.delete("/{public_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project_endpoint(
    public_id: UUID,
    db: AsyncSession = Depends(get_pg_db),
    current_user: User = Depends(get_current_user),
):
    await delete_project(public_id, db, current_user)
