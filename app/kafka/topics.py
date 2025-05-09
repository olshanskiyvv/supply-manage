from typing import Self, Optional, Any, Type

from aiokafka.admin import NewTopic, AIOKafkaAdminClient

from app.config import get_kafka_url

KAFKA_TOPICS = [
    NewTopic(name='supplier_price_updates', num_partitions=1, replication_factor=1),
    NewTopic(name='product_remaining_stock_updates', num_partitions=1, replication_factor=1),
    NewTopic(name='supplier_order_updates', num_partitions=1, replication_factor=1),
    NewTopic(name='factory_order_updates', num_partitions=1, replication_factor=1),
]

class KafkaTopicManager:
    async def __aenter__(self) -> Self:
        self.admin_client = AIOKafkaAdminClient(bootstrap_servers=get_kafka_url())
        await self.admin_client.start()
        return self

    async def __aexit__(
            self, exc_type: Optional[Type[BaseException]], exc_val: Optional[BaseException], exc_tb: Any
    ) -> None:
        if self.admin_client:
            await self.admin_client.close()
        return None

    async def create_topics(self, topics: list[NewTopic]) -> None:
        if not self.admin_client:
            raise RuntimeError("Admin client is not started")
        existing_topics = await self.admin_client.list_topics()
        topics_to_create = [topic for topic in topics if topic.name not in existing_topics]

        if not topics_to_create:
            return
        print('Creating topics')
        await self.admin_client.create_topics(new_topics=topics_to_create)
        return None


topic_manager = KafkaTopicManager()