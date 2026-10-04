from sqlalchemy import BigInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from ..database import Base


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    name_tr: Mapped[str] = mapped_column(String(120), default="")
    slug: Mapped[str] = mapped_column(String(50), unique=True)
