from enum import Enum

from sqlalchemy import Text
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base, int_pk


class MeasureUnit(str, Enum):
    UNIT = 'Штуки'
    SET = 'Наборы'
    KIT = 'Комплекты'

class Product(Base):
    id: Mapped[int_pk]
    title: Mapped[str]
    description: Mapped[str] = mapped_column(Text, nullable=False)
    available: Mapped[int]
    unit: Mapped[MeasureUnit]

    extend_existing = True

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id})"



