import asyncio
import json
from asyncio import AbstractEventLoop, Task
from typing import Callable, Dict, Coroutine, Any

from aiokafka import AIOKafkaConsumer

from app.config import get_kafka_url
from app.kafka.schemas import KafkaNewSupplierPrice, KafkaNewProductAvailable, KafkaNewOrderSupplierStatus
from app.orders.services import update_supplier_order_status
from app.products.service import update_available_stock
from app.suppliers.service import update_supplier_product_price


class KafkaConsumer:
    def __init__(self, loop: AbstractEventLoop) -> None:
        self._loop = loop
        self._consumer = AIOKafkaConsumer(
            bootstrap_servers=get_kafka_url(),
            group_id="fastapi-consumer",
            loop=self._loop,
            auto_offset_reset="earliest",
        )
        self._handlers: Dict[str, Callable[[str, dict[Any, Any]], Coroutine[Any, Any, None]]] = {}
        self._task: Task[None] | None = None

    def register_handler(self, topic: str, handler: Callable[[str, dict[Any, Any]], Coroutine[Any, Any, None]]) -> None:
        self._handlers[topic] = handler

    async def start(self) -> None:
        await self._consumer.start()
        self._consumer.subscribe(topics=list(self._handlers.keys()))
        self._task = asyncio.create_task(self._consume())

    async def stop(self) -> None:
        if self._task:
            self._task.cancel()
        if self._consumer:
            await self._consumer.stop()

    async def _consume(self) -> None:
        try:
            async for msg in self._consumer:
                topic = msg.topic
                value = json.loads(msg.value.decode("utf-8"))
                key = msg.key
                if isinstance(key, bytes):
                    key = key.decode("utf-8")
                handler = self._handlers.get(topic)
                if handler:
                    try:
                        await handler(key, value)
                    except Exception as e:
                        print(e)
        except asyncio.CancelledError:
            pass


class PriceConsumer:
    def __init__(self, kafka: KafkaConsumer):
        self._kafka = kafka
        self._kafka.register_handler("supplier_price_updates", self.handle_price_update)

    async def handle_price_update(self, _: str, data: dict) -> None:
        price_event = KafkaNewSupplierPrice.model_validate(data)
        await update_supplier_product_price(price_event)


class StockConsumer:
    def __init__(self, kafka: KafkaConsumer):
        self._kafka = kafka
        self._kafka.register_handler("product_remaining_stock_updates", self.handle_stock_update)

    async def handle_stock_update(self, _: str, data: dict) -> None:
        stock_event = KafkaNewProductAvailable.model_validate(data)
        await update_available_stock(stock_event)


class OrderConsumer:
    def __init__(self, kafka: KafkaConsumer):
        self._kafka = kafka
        self._kafka.register_handler("supplier_order_updates", self.handle_order_status_update)

    async def handle_order_status_update(self, key: str, data: dict) -> None:
        order_event = KafkaNewOrderSupplierStatus.model_validate(data)
        await update_supplier_order_status(order_event)
