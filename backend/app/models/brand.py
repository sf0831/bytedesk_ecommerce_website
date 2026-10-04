from sqlalchemy import BigInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from ..database import Base


class Brand(Base):
    __tablename__ = "brands"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    slug: Mapped[str] = mapped_column(String(50), unique=True)
