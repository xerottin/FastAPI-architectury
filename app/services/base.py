from typing import TypeVar
from uuid import UUID

from core.exceptions import AppException
from db.base import Base
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar("T", bound=Base)


async def get_by_public_id(
    db: AsyncSession,
    model: type[T],
    public_id: UUID,
    require_active: bool = True,
) -> T:
    query = select(model).where(model.public_id == public_id)

    if require_active and hasattr(model, "is_active"):
        query = query.where(model.is_active == True)  # noqa: E712

    result = await db.scalar(query)

    if not result:
        raise AppException(
            code=f"{model.__name__.upper()}_NOT_FOUND",
            i18n_key=f"errors.{model.__name__.upper()}_not_found",
            status_code=404,
            detail=f"{model.__name__} not found",
        )

    return result


async def get_by_id(
    db: AsyncSession,
    model: type[T],
    id: int,
    require_active: bool = True,
) -> UUID:
    query = select(model).where(model.id == id)

    if require_active and hasattr(model, "is_active"):
        query = query.where(model.is_active == True)  # noqa: E712

    result = await db.scalar(query)

    if not result:
        raise AppException(
            code=f"{model.__name__.upper()}_NOT_FOUND",
            i18n_key=f"errors.{model.__name__.upper()}_not_found",
            status_code=404,
            detail=f"{model.__name__} not found",
        )
    return result
