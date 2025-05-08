from app.orders.dao import OrdersDAO, OrderProductDAO
from app.orders.models import Order, Status
from app.orders.schemas import SFullOrder, SOrderRB, SOrder, SOrderProductRB


def order_to_full_schema(order: Order) -> SFullOrder:
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


async def create_new_order(user_id: int,
                           order: SOrderRB) -> SOrder:
    order_dict = order.model_dump()
    order_dict['user_id'] = user_id
    order_dict['status'] = Status.FORMING
    order_dict['total_cost'] = None
    order_dict['cancel_comment'] = None

    order = await OrdersDAO.add(**order_dict)
    return SOrder.model_validate(order, from_attributes=True)


async def add_products_to_order(order_id: int,
                                products: list[SOrderProductRB]) -> SFullOrder:
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
    return order_to_full_schema(order)


async def delete_products_from_order(order_id: int,
                                     products: list[int]) -> SFullOrder:
    await OrderProductDAO.delete_by_order_id_and_product_ids(order_id, products)
    order = await OrdersDAO.find_full_by_id(order_id)
    return order_to_full_schema(order)