import logging
from uuid import UUID

from core.exceptions import AppException
from services.base import get_by_public_id
from models import Project, User
from schemas.project import ProjectCreate, ProjectUpdate
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


async def get_owned_project(
    public_id: UUID,
    db: AsyncSession,
    user_id: int,
) -> Project:
    project = await get_by_public_id(db, Project, public_id)

    if project.owner_id != user_id:
        raise AppException(
            code="PROJECT_NOT_FOUND",
            i18n_key="errors.project_not_found",
            status_code=404,
            detail="Project not found",
        )

    return project


async def get_project_id_by_public_id(
    public_id: UUID,
    db: AsyncSession,
):
    project_public_id = (
        await db.execute(
            select(Project).where(
                Project.public_id == public_id,
                Project.is_active.is_(True),
            )
        )
    ).scalar_one_or_none()
    if not project_public_id:
        raise AppException(
            code="INTERNAL_ERROR",
            i18n_key="errors.internal_server_error",
            status_code=500,
            detail="Project not found",
        )
    return project_public_id.id


async def create_project(
    payload: ProjectCreate,
    db: AsyncSession,
    current_user: User,
) -> Project:
    exist_project = await db.scalar(
        select(Project).where(
            Project.name == payload.name,
            Project.owner_id == current_user.id,
            Project.is_active,
        )
    )

    if exist_project:
        raise AppException(
            code="PROJECT_NAME_EXISTS",
            i18n_key="errors.project_name_exists",
            status_code=409,
            detail="Project with this name already exists",
        )

    try:
        project = Project(
            name=payload.name,
            description=payload.description,
            owner_id=current_user.id,
        )

        db.add(project)
        await db.commit()
        await db.refresh(project)

        return project

    except AppException:
        raise
    except Exception as e:
        await db.rollback()
        logger.exception("Error creating project")
        raise AppException(
            code="INTERNAL_ERROR",
            i18n_key="errors.internal_server_error",
            status_code=500,
            detail="Internal server error",
        ) from e


async def list_projects(
    db: AsyncSession,
    current_user: User,
) -> list[Project]:
    result = await db.execute(
        select(Project).where(
            Project.owner_id == current_user.id,
            Project.is_active.is_(True),
        )
    )

    return result.scalars().all()


async def my_project(
    db: AsyncSession,
    current_user: User,
) -> Project:
    result = await db.execute(
        select(Project).where(
            Project.id == current_user.project_id,
            Project.is_active,
        )
    )
    return result.scalar_one_or_none()


async def get_project(
    public_id: UUID,
    db: AsyncSession,
    current_user: User,
) -> Project:
    return await get_owned_project(
        public_id=public_id,
        db=db,
        user_id=current_user.id,
    )


async def update_project(
    public_id: UUID,
    payload: ProjectUpdate,
    db: AsyncSession,
    current_user: User,
) -> Project:
    project = await get_owned_project(
        public_id=public_id,
        db=db,
        user_id=current_user.id,
    )

    try:
        update_data = payload.model_dump(exclude_unset=True)

        if "owner_public_id" in update_data:
            owner_public_id = update_data.pop("owner_public_id")
            owner = await get_by_public_id(db, User, owner_public_id)
            update_data["owner_id"] = owner.id

        for key, value in update_data.items():
            setattr(project, key, value)

        await db.commit()
        await db.refresh(project)

        return project

    except AppException:
        raise
    except Exception as e:
        await db.rollback()
        logger.exception("Error updating project")
        raise AppException(
            code="INTERNAL_ERROR",
            i18n_key="errors.internal_server_error",
            status_code=500,
            detail="Internal server error",
        ) from e


async def delete_project(
    public_id: UUID,
    db: AsyncSession,
    current_user: User,
):
    project = await get_owned_project(
        public_id=public_id,
        db=db,
        user_id=current_user.id,
    )

    if not project.is_active:
        raise AppException(
            code="PROJECT_ALREADY_DEACTIVATED",
            i18n_key="errors.project_already_deactivated",
            status_code=400,
            detail="Project already deactivated",
        )

    try:
        project.is_active = False
        await db.commit()

    except AppException:
        raise
    except Exception as e:
        await db.rollback()
        logger.exception("Error deleting project")
        raise AppException(
            code="INTERNAL_ERROR",
            i18n_key="errors.internal_server_error",
            status_code=500,
            detail="Internal server error",
        ) from e
