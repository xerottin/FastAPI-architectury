from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import BaseModel


class User(BaseModel):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=True)
    role: Mapped[str] = mapped_column(String(50), default="default_user")

    project_id: Mapped[int | None] = mapped_column(
        ForeignKey("projects.id", ondelete="SET NULL"),
        index=True, # if need
    )

    project: Mapped["Project | None"] = relationship(
        "Project",
        back_populates="users",
        foreign_keys=[project_id],
    )

    owned_projects: Mapped[list["Project"]] = relationship(
        "Project",
        back_populates="owner",
        foreign_keys="Project.owner_id",
        lazy="selectin",
    )
