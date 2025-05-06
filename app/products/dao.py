from typing import Sequence

from sqlalchemy import select

from app.dao.base import BaseDAO
from app.database import async_session_maker
from app.products.models import Product
from app.products.schemas import SProductFilters


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



