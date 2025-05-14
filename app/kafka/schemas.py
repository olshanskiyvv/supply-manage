import json
from datetime import datetime
from enum import Enum
from typing import Any, Optional, Self
from uuid import UUID

from pydantic import BaseModel, Field, model_validator


class KafkaEventBase(BaseModel):
    def to_kafka_bytes(self) -> bytes:
        def default_serializer(obj: Any) -> Any:
            if isinstance(obj, UUID):
                return str(obj)
            if isinstance(obj, datetime):
                return obj.isoformat()
            raise TypeError(f"Type {type(obj)} not serializable")

        return json.dumps(
            self.model_dump(exclude_none=True, exclude_unset=True),
            default=default_serializer
        ).encode("utf-8")


class KafkaNewSupplierPrice(BaseModel):
    """
    Message sample

    {
        "ogrn": "159317825",
        "product_code": "156562",
        "price": 100
    }
    """
    ogrn: str = Field(..., description='ОГРН поставщика')
    product_code: str = Field(..., description='Код товара поставщика')
    price: int = Field(..., ge=1, description='Новая цена')


class KafkaNewProductAvailable(BaseModel):
    """
    Message sample

    {
        "product_id": 2,
        "available": 1000
    }
    """
    product_id: int = Field(..., description='Идентификатор продукта')
    available: int = Field(..., ge=0, description='Новый остаток на складе')


class KafkaOrderStatus(str, Enum):
    SEND_TO_SUPPLIER = "SEND_TO_SUPPLIER"
    IN_PROGRESS = "IN_PROGRESS"
    IN_DELIVERY = "IN_DELIVERY"
    DELIVERED = "DELIVERED"
    CANCELED = "CANCELED"


class KafkaNewOrderSupplierStatus(BaseModel):
    """
    Message samples

    {
      "order_number": "bf1dd005-1824-49b0-a7f9-1fb5dbcd573a",
      "status": "IN_PROGRESS",
      "cancel_comment": null
    }

    {
      "order_number": "bf1dd005-1824-49b0-a7f9-1fb5dbcd573a",
      "status": "CANCELED",
      "cancel_comment": "Мы передумали"
    }
    """
    order_number: UUID = Field(..., description='')
    status: KafkaOrderStatus = Field(..., description='')
    cancel_comment: Optional[str] = Field(..., description='')

    @model_validator(mode='after')
    def cancel_validator(self) -> Self:
        if self.status == KafkaOrderStatus.CANCELED and not self.cancel_comment:
            raise ValueError("cancel_comment cannot be None if status is CANCELLED_BY_SUPPLIER")
        return self

class MessageType(str, Enum):
    NEW_STATUS = 'NEW_STATUS'
    NEW_ORDER = 'NEW_ORDER'

class KafkaProduct(BaseModel):
    title: str = Field(..., description='Наименование товара')
    code: str = Field(..., description='Код товара у поставщика')
    amount: int = Field(..., gt=0, description='Количество в заказе')
    price: int = Field(..., gt=0, description='Цена за единицу')
    total_cost: int = Field(..., gt=0, description='Итоговая стоимость')

class KafkaOrder(KafkaEventBase):
    number: UUID = Field(..., description='Номер заказа')
    # supplier: SSupplier = Field(..., description='Поставщик')
    products: list[KafkaProduct] = Field(..., description='Товары')
    total_cost: int = Field(..., ge=1, description='Итоговая стоимость')

class KafkaNewOrderStatus(KafkaEventBase):
    """
    Message sample

    {
      "event_type": "NEW_ORDER",
      "order_number": "bf1dd005-1824-49b0-a7f9-1fb5dbcd573a",
      "new_order": {
        "number": "bf1dd005-1824-49b0-a7f9-1fb5dbcd573a",
        "products": [
          {
            "title": "Гвозди 100 мм",
            "code": "156562",
            "amount": 10,
            "price": 15,
            "total_cost": 150
          },
          {
            "title": "Гвозди 50 мм",
            "code": "1717846",
            "amount": 20,
            "price": 11,
            "total_cost": 220
          }
        ],
        "total_cost": 370
      }
    }
    """
    event_type: MessageType = Field(..., description='Тип события')
    order_number: UUID = Field(..., description='Номер заказа')
    new_order: Optional[KafkaOrder] = Field(..., description='Заказ')
    new_status: Optional[KafkaOrderStatus] = Field(..., description='Новый статус')

    @model_validator(mode='after')
    def cancel_validator(self) -> Self:
        if self.event_type == MessageType.NEW_ORDER and not self.new_order:
            raise ValueError("new_order cannot be None if event_type is NEW_ORDER")
        if self.event_type == MessageType.NEW_STATUS and not self.new_status:
            raise ValueError("new_status cannot be None if event_type is NEW_STATUS")
        return self

