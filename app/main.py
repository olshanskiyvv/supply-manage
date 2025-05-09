import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI

from app.auth.api import router as auth_router
from app.kafka.topics import KafkaTopicManager, KAFKA_TOPICS
from app.products.api import router as products_router
from app.suppliers.api import router as suppliers_router
from app.orders.api import router as orders_router

from app.kafka.consumers import KafkaConsumer, PriceConsumer, StockConsumer, OrderConsumer
from app.kafka.producers import kafka_producer


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None, None]:
    async with KafkaTopicManager() as manager:
        await manager.create_topics(KAFKA_TOPICS)
    loop = asyncio.get_event_loop()
    kafka_consumer = KafkaConsumer(loop)
    _ = PriceConsumer(kafka_consumer)
    _ = StockConsumer(kafka_consumer)
    _ = OrderConsumer(kafka_consumer)
    try:
        await kafka_consumer.start()
        await kafka_producer.start()
        yield
    finally:
        await kafka_consumer.stop()
        await kafka_producer.stop()

app = FastAPI(lifespan=lifespan)

app.include_router(auth_router)
app.include_router(products_router)
app.include_router(suppliers_router)
app.include_router(orders_router)


