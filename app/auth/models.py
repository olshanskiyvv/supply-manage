from enum import Enum

from sqlalchemy import text
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base, str_uniq, int_pk

class Role(str, Enum):
    ADMIN = "admin"
    USER = "user"


class User(Base):
    id: Mapped[int_pk]
    email: Mapped[str_uniq]
    name: Mapped[str]
    surname: Mapped[str]
    patronymic: Mapped[str | None]
    password: Mapped[str]
    role: Mapped[Role]

    extend_existing = True

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id})"