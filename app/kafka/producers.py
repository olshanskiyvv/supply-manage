from aiokafka import AIOKafkaProducer

from app.config import get_kafka_url
from app.kafka.schemas import KafkaEventBase


class KafkaProducer:
    def __init__(self):
        self._producer = AIOKafkaProducer(bootstrap_servers=get_kafka_url())

    async def start(self) -> None:
        await self._producer.start()
        return None

    async def stop(self) -> None:
        if self._producer:
            await self._producer.stop()
        return None

    async def send(self, key: str, message: KafkaEventBase) -> None:
        if not self._producer:
            raise RuntimeError("Kafka producer not started")
        await self._producer.send_and_wait(
            topic='factory_order_updates',
            key=key.encode('utf-8'),
            value=message.to_kafka_bytes(),
        )
        return None

kafka_producer = KafkaProducer()
