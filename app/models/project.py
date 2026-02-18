from sqlalchemy import String, ForeignKey

from models.base import BaseModel
from sqlalchemy.orm import Mapped, mapped_column, relationship

class Project(BaseModel):
    __tablename__ = "projects"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=True)

    owner_id: Mapped[int] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
            use_alter=True,
            name="fk_projects_owner_id_users",
        ),
        index=True,
        nullable=True,
    )

    owner: Mapped["User"] = relationship(
        "User",
        back_populates="owned_projects",
        foreign_keys=[owner_id],
    )


    users: Mapped[list["User"]] = relationship(
        "User",
        back_populates="project",
        foreign_keys="User.project_id",
        lazy="selectin",
    )


