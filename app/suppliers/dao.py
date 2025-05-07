from typing import Sequence

from sqlalchemy import select, delete as sqlalchemy_delete
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload

from app.dao.base import BaseDAO
from app.database import async_session_maker
from app.suppliers.models import Supplier, SupplierProduct
from app.suppliers.schemas import SSupplierFilters


class SuppliersDAO(BaseDAO[Supplier]):
    model = Supplier

    @classmethod
    async def find_all_by_filters(cls, filters: SSupplierFilters | None) -> Sequence[Supplier]:
        async with async_session_maker() as session:
            query = (
                select(cls.model)
                .where(cls.model.title.icontains(filters.title))
            )
            result = await session.execute(query)
            return result.scalars().all()

    @classmethod
    async def find_full_by_id(cls, supplier_id: int) -> Supplier | None:
        async with async_session_maker() as session:
            query = (
                select(cls.model)
                .options(
                    joinedload(cls.model.products)
                    .options(joinedload(SupplierProduct.product))
                )
                .where(cls.model.id == supplier_id)
            )
            result = await session.execute(query)
            return result.scalars().unique().one_or_none()


class SupplierProductDAO(BaseDAO[SupplierProduct]):
    model = SupplierProduct

    @classmethod
    async def delete_by_supplier_id_and_product_ids(cls,
                                                    supplier_id: int,
                                                    product_ids: list[int]
                                                    ) -> int:
        async with async_session_maker() as session:
            async with session.begin():
                query = (
                    sqlalchemy_delete(cls.model)
                    .filter_by(supplier_id=supplier_id)
                    .filter(cls.model.product_id.in_(product_ids))
                )
                result = await session.execute(query)
                try:
                    await session.commit()
                except SQLAlchemyError as e:
                    await session.rollback()
                    raise e
                return result.rowcount
