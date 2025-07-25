from sqlalchemy import select, delete as sqlalchemy_delete
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload, contains_eager

from app.dao.base import BaseDAO
from app.database import async_session_maker
from app.orders.models import Order, OrderProduct, Status


class OrdersDAO(BaseDAO[Order]):
    model = Order

    @classmethod
    async def find_all_by_user_id(cls,
                                  user_id: int | None):
        async with async_session_maker() as session:
            query = (
                select(cls.model)
                .options(joinedload(cls.model.supplier))
            )
            if user_id:
                query = query.where(cls.model.user_id == user_id)
            result = await session.execute(query)
            return result.scalars().all()

    @classmethod
    async def find_full_by_id(cls, order_id: int) -> Order | None:
        async with async_session_maker() as session:
            query = (
                select(cls.model)
                .options(
                    joinedload(cls.model.products)
                    .options(joinedload(OrderProduct.product)),
                    joinedload(cls.model.supplier),
                    joinedload(cls.model.user),
                )
                .where(cls.model.id == order_id)
            )
            result = await session.execute(query)
            return result.scalars().unique().one_or_none()




    @classmethod
    async def set_status(cls, order_id: int, status: Status, comment: str | None = None) -> Order:
        count = await cls.update({'id': order_id}, status=status, cancel_comment=comment)
        if count == 0:
            raise ValueError(f'Something went wrong while setting status {status} for order with id={order_id}')
        return await cls.find_full_by_id(order_id)


class OrderProductDAO(BaseDAO[OrderProduct]):
    model = OrderProduct

    @classmethod
    async def delete_by_order_id_and_product_ids(cls,
                                                 order_id: int,
                                                 product_ids: list[int]) -> int:
        async with async_session_maker() as session:
            async with session.begin():
                query = (
                    sqlalchemy_delete(cls.model)
                    .filter_by(order_id=order_id)
                    .filter(cls.model.product_id.in_(product_ids))
                )
                result = await session.execute(query)
                try:
                    await session.commit()
                except SQLAlchemyError as e:
                    await session.rollback()
                    raise e
                return result.rowcount
