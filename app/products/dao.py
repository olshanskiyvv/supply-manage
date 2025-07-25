from typing import Sequence

from sqlalchemy import select
from sqlalchemy.orm import joinedload, contains_eager

from app.dao.base import BaseDAO
from app.database import async_session_maker
from app.orders.models import OrderProduct
from app.products.models import Product
from app.products.schemas import SProductFilters
from app.suppliers.models import SupplierProduct


class ProductDAO(BaseDAO[Product]):
    model = Product

    @classmethod
    async def find_all_by_filters(cls, filters: SProductFilters | None) -> Sequence[Product]:
        async with async_session_maker() as session:
            query = (
                select(cls.model)
                .where(cls.model.title.icontains(filters.title))
            )
            result = await session.execute(query)
            return result.scalars().all()

    @classmethod
    async def find_all_full_by_filters(cls, filters: SProductFilters | None) -> Sequence[Product]:
        async with async_session_maker() as session:
            query = (
                select(cls.model)
                .options(
                    joinedload(cls.model.suppliers)
                    .options(joinedload(SupplierProduct.supplier))
                )
                .where(cls.model.title.icontains(filters.title))
            )
            result = await session.execute(query)
            return result.scalars().unique().all()

    @classmethod
    async def update_available_stock(cls, product_id: int, available: int) -> int:
        count = await cls.update({'id': product_id}, available=available)
        return count

    @classmethod
    async def find_full_by_order_id_and_supplier_id(cls, order_id: int, supplier_id: int) -> list[Product]:
        async with async_session_maker() as session:
            query = (
                select(cls.model)
                .join(cls.model.suppliers)
                .options(contains_eager(cls.model.suppliers))
                .join(cls.model.orders)
                .options(contains_eager(cls.model.orders))
                .where(OrderProduct.order_id == order_id,
                       SupplierProduct.supplier_id == supplier_id)
            )
            result = await session.execute(query)
            return result.scalars().unique().all()





