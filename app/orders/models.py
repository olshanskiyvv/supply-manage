from enum import Enum
from uuid import UUID

from sqlalchemy import ForeignKey, func, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.util import rw_hybridproperty

from app.database import Base, int_pk, str_uniq


class Status(str, Enum):
    FORMING = 'Формируется'
    CREATED = 'Создан'
    PAYED = 'Оплачен'
    SEND_TO_SUPPLIER = 'Направлен поставщику'
    IN_PROCESS = 'Взят в работу'
    IN_DELIVERY = 'Передан в доставку'
    DELIVERED = 'Доставлен'
    COMPLETED = 'Выполнен'
    CANCELLED_BY_SUPPLIER = 'Отменен поставщиком'
    CANCELLED_BY_FACTORY = 'Отменен заводом'


class Order(Base):
    id: Mapped[int_pk]
    number: Mapped[UUID] = mapped_column(server_default=func.gen_random_uuid())
    status: Mapped[Status]
    cancel_comment: Mapped[str] = mapped_column(Text, nullable=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    supplier_id: Mapped[int] = mapped_column(ForeignKey('suppliers.id'), nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="orders")
    supplier: Mapped["Supplier"] = relationship("Supplier", back_populates="orders")
    products: Mapped[list["OrderProduct"]] = relationship("OrderProduct", back_populates="order")

    extend_existing = True

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id})"


class OrderProduct(Base):
    __tablename__ = "order_products"
    order_id: Mapped[int] = mapped_column(ForeignKey('orders.id'), primary_key=True)
    product_id: Mapped[str] = mapped_column(ForeignKey('products.id'), primary_key=True)
    amount: Mapped[int]

    order: Mapped["Order"] = relationship("Order", back_populates="products")
    product: Mapped["Product"] = relationship("Product", back_populates="orders")

    extend_existing = True

    def __repr__(self):
        return f'{self.__class__.__name__}(order_id={self.order_id}, product_id={self.product_id})'


