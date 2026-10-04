from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from ..database import Base


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    username: Mapped[str] = mapped_column(String(150))
    email: Mapped[str] = mapped_column(String(254))
    password: Mapped[str] = mapped_column(String(128))
    first_name: Mapped[str] = mapped_column(String(150), default="")
    last_name: Mapped[str] = mapped_column(String(150), default="")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_staff: Mapped[bool] = mapped_column(Boolean, default=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)
    date_joined: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    last_login: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    auth_version: Mapped[int] = mapped_column(Integer, default=0)
