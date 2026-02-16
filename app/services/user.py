from app.models.base import BaseModel


class User(BaseModel):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=True)
    job_title: Mapped[str] = mapped_column(String(255), nullable=True)
    external_user_id: Mapped[str] = mapped_column(String(255), nullable=True)