from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base, int_pk, str_uniq


class Supplier(Base):
    id: Mapped[int_pk]
    ogrn: Mapped[str_uniq]
    title: Mapped[str_uniq]
    topic_name_base: Mapped[str_uniq]
    admin_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='SET NULL'), nullable=True)

    products: Mapped[list["SupplierProduct"]] = relationship(
        "SupplierProduct",
        back_populates="supplier",
    )

    extend_existing = True

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id})"

class SupplierProduct(Base):
    __tablename__ = "supplier_products"
    supplier_id: Mapped[int] = mapped_column(ForeignKey('suppliers.id'), primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey('products.id'), primary_key=True)
    supplier_product_id: Mapped[str]
    price: Mapped[int]

    supplier: Mapped['Supplier'] = relationship(
        'Supplier',
        back_populates="products",
    )
    product: Mapped['Product'] = relationship(
        'Product',
        back_populates="suppliers",
    )

    extend_existing = True

    def __repr__(self):
        return f'{self.__class__.__name__}(supplier_id={self.supplier_id}, product_id={self.product_id})'