from enum import Enum

from sqlalchemy.orm import Mapped, relationship
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

    orders: Mapped[list["Order"]] = relationship("Order", back_populates="user")

    extend_existing = True

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id})"