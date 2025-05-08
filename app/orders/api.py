from fastapi import APIRouter, Depends, HTTPException

from app.auth.dependencies import get_current_user, get_current_admin_user
from app.auth.models import User, Role
from app.orders.dao import OrdersDAO, OrderProductDAO
from app.orders.models import Status, Order
from app.orders.schemas import SOrder, SOrderRB, SFullOrder, SOrderProductRB
from app.orders.services import order_to_full_schema, create_new_order, add_products_to_order, \
    delete_products_from_order

router = APIRouter(prefix='/orders', tags=['Orders'])


@router.get('/')
async def all_orders(current_user: User = Depends(get_current_user)) -> list[SOrder]:
    user_id = current_user.id
    if current_user.role == Role.ADMIN:
        user_id = None
    orders = await OrdersDAO.find_all_by_user_id(user_id)
    return orders


@router.post('/')
async def create_order(order: SOrderRB,
                       current_user: User = Depends(get_current_user)) -> SOrder:
    order = await create_new_order(current_user.id, order)
    return order


def _check_access_to_order(order: Order, user: User) -> bool:
    return user.role == Role.ADMIN or order.user_id == user.id


@router.get('/{order_id}/')
async def get_order_by_id(order_id: int,
                          current_user: User = Depends(get_current_user)) -> SFullOrder:
    order = await OrdersDAO.find_full_by_id(order_id)
    if order is None or not _check_access_to_order(order, current_user):
        raise HTTPException(
            status_code=404,
            detail=f'Order with {order_id=} not found.',
        )
    return order_to_full_schema(order)


@router.post('/{order_id}/products')
async def add_ordered_products(order_id: int,
                               products: list[SOrderProductRB],
                               current_user: User = Depends(get_current_user)) -> SFullOrder:
    order = await OrdersDAO.find_full_by_id(order_id)
    if order is None or not _check_access_to_order(order, current_user):
        raise HTTPException(
            status_code=404,
            detail=f'Order with {order_id=} not found.',
        )
    if order.status != Status.FORMING:
        raise HTTPException(
            status_code=400,
            detail=f'Order with {order_id=} is already formed and cannot be modified.',
        )

    order = await add_products_to_order(order_id, products)
    return order


@router.delete('/{order_id}/products/')
async def delete_ordered_products(order_id: int,
                                  products: list[int],
                                  current_user: User = Depends(get_current_admin_user)) -> SFullOrder:
    order = await OrdersDAO.find_full_by_id(order_id)
    if order is None or not _check_access_to_order(order, current_user):
        raise HTTPException(
            status_code=404,
            detail=f'Order with {order_id=} not found.',
        )
    if order.status != Status.FORMING:
        raise HTTPException(
            status_code=400,
            detail=f'Order with {order_id=} is already formed and cannot be modified.',
        )
    if len(products) == 0:
        raise HTTPException(
            status_code=400,
            detail=f"List of products to delete is empty",
        )

    order = await delete_products_from_order(order_id, products)
    return order

