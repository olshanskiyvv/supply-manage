from app.kafka.producers import kafka_producer
from app.kafka.schemas import KafkaProduct, KafkaOrder, KafkaNewOrderStatus, MessageType, KafkaNewOrderSupplierStatus, \
    KafkaOrderStatus
from app.orders.dao import OrdersDAO, OrderProductDAO
from app.orders.models import Order, Status
from app.orders.schemas import SFullOrder, SOrderRB, SOrder, SOrderProductRB
from app.products.dao import ProductDAO
from app.products.models import Product
from app.suppliers.dao import SuppliersDAO


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


class InvalidStatusError(Exception):
    pass


async def find_not_supplied_order_products(order: Order) -> set[Product]:
    full_order = await OrdersDAO.find_full_by_id(order.id)
    full_supplier = await SuppliersDAO.find_full_by_id(order.supplier_id)

    supplied_product_ids = {
        prod.product_id
        for prod in full_supplier.products
    }
    not_supplied_product_ids = set()
    for prod in full_order.products:
        if prod.product_id not in supplied_product_ids:
            not_supplied_product_ids.add(prod.product)

    return not_supplied_product_ids


async def send_new_order_event(order: Order) -> None:
    order = await OrdersDAO.find_full_by_id(order.id)
    full_products = await ProductDAO.find_full_by_order_id_and_supplier_id(order.id, order.supplier_id)
    products = [
        KafkaProduct(
            title=prod.title,
            code=prod.suppliers[0].supplier_product_id,
            price=prod.suppliers[0].price,
            amount=prod.orders[0].amount,
            total_cost=prod.suppliers[0].price * prod.orders[0].amount
        )
        for prod in full_products
    ]
    total_cost = sum(map(lambda prod: prod.total_cost, products))
    order_data = KafkaOrder(
        number=order.number,
        products=products,
        total_cost=total_cost,
    )
    event = KafkaNewOrderStatus(
        event_type=MessageType.NEW_ORDER,
        order_number=order.number,
        new_order=order_data,
        new_status=None,
    )
    await kafka_producer.send(order.supplier.ogrn, event)


async def update_supplier_order_status(order_status_event: KafkaNewOrderSupplierStatus) -> None:
    order = await OrdersDAO.find_one_or_none(number=order_status_event.order_number)
    if not order:
        raise ValueError(f'Order with number={order_status_event.order_number} not found')

    status_mapper = {
        KafkaOrderStatus.SEND_TO_SUPPLIER: Status.SEND_TO_SUPPLIER,
        KafkaOrderStatus.IN_PROGRESS: Status.IN_PROCESS,
        KafkaOrderStatus.IN_DELIVERY: Status.IN_DELIVERY,
        KafkaOrderStatus.DELIVERED: Status.DELIVERED,
        KafkaOrderStatus.CANCELED: Status.CANCELLED_BY_SUPPLIER,
    }
    new_status = status_mapper[order_status_event.status]
    await set_next_status(order, new_status, order_status_event.cancel_comment)


async def set_next_status(order: Order, status: Status, cancel_comment: str | None = None) -> Order:
    current_status = order.status
    if current_status == status:
        return order
    valid_prev_statuses: dict[Status, set[Status]] = {
        Status.CREATED: {Status.FORMING},
        Status.PAYED: {Status.CREATED},
        Status.SEND_TO_SUPPLIER: {Status.CREATED},
        Status.IN_PROCESS: {Status.SEND_TO_SUPPLIER},
        Status.IN_DELIVERY: {Status.IN_PROCESS},
        Status.DELIVERED: {Status.IN_DELIVERY},
        Status.COMPLETED: {Status.DELIVERED},
        Status.CANCELLED_BY_FACTORY: {
            Status.CREATED,
            Status.PAYED,
            Status.SEND_TO_SUPPLIER,
            Status.IN_PROCESS,
        },
        Status.CANCELLED_BY_SUPPLIER: {
            Status.SEND_TO_SUPPLIER,
            Status.IN_PROCESS,
        },
    }
    if current_status not in valid_prev_statuses[status]:
        raise InvalidStatusError(
            f'Order with id={order.id} cannot switch status from {current_status} to {status}'
        )
    if status in (Status.CANCELLED_BY_FACTORY, Status.CANCELLED_BY_SUPPLIER):
        if cancel_comment is None:
            raise InvalidStatusError(
                f'Cancel comment must be set for status {status}'
            )
    else:
        cancel_comment = None

    order = await OrdersDAO.set_status(order.id, status, comment=cancel_comment)
    return order
