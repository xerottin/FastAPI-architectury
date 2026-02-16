import uuid
from datetime import datetime

from app.db.base import Base
from sqlalchemy import Boolean, DateTime, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func


class BaseModel(Base):
    __abstract__ = True
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    public_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        default=uuid.uuid4,
        unique=True,
        index=True,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
