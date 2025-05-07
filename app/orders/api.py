from fastapi import APIRouter, Depends, HTTPException

from app.auth.dependencies import get_current_user, get_current_admin_user
from app.auth.models import User, Role
from app.orders.dao import OrdersDAO, OrderProductDAO
from app.orders.models import Status, Order
from app.orders.schemas import SOrder, SOrderRB, SFullOrder, SOrderProductRB

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
    order_dict = order.model_dump()
    order_dict['user_id'] = current_user.id
    order_dict['status'] = Status.FORMING
    order_dict['cancel_comment'] = None

    order = await OrdersDAO.add(**order_dict)
    order = await OrdersDAO.find_full_by_id(order.id)
    return order


def _order_to_full_schema(order: Order) -> SFullOrder:
    order_dict = order.to_dict()
    order_dict['supplier'] = order.supplier.to_dict()
    order_dict['products'] = [
        {
            **prod.to_dict(),
            'title': prod.product.title,
        }
        for prod in order.products
    ]
    return SFullOrder(**order_dict)


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
    return _order_to_full_schema(order)


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
    new_products = [
        {
            'product_id': prod.product_id,
            'order_id': order_id,
            'amount': prod.amount,
        }
        for prod in products
    ]
    await OrderProductDAO.add_all(*new_products)
    order = await OrdersDAO.find_full_by_id(order_id)
    return _order_to_full_schema(order)


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
    await OrderProductDAO.delete_by_order_id_and_product_ids(order_id, products)
    order = await OrdersDAO.find_full_by_id(order_id)
    return _order_to_full_schema(order)

