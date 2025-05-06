from typing import Sequence

from sqlalchemy import select

from app.dao.base import BaseDAO
from app.database import async_session_maker
from app.suppliers.models import Supplier
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

