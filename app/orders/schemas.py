from uuid import UUID

from pydantic import BaseModel, Field

from app.auth.schemas import SUser
from app.orders.models import Status
from app.suppliers.schemas import SSupplier


class SOrder(BaseModel):
    id: int = Field(..., description='Идентификатор')
    number: UUID = Field(..., description='Номер заказа')
    status: Status = Field(..., description='Статус заказа')
    cancel_comment: str | None = Field('', description='Комментарий к отмене')
    supplier: SSupplier = Field(..., description='Поставщик')

class SOrderAdmin(SOrder):
    user: SUser = Field(..., description='Пользователь')

class SOrderRB(BaseModel):
    supplier_id: int = Field(..., description='Идентификатор поставщика')

class SOrderFilter(BaseModel):
    supplier: str = Field('', description='Поставщик')

class SOrderProductRB(BaseModel):
    product_id: int = Field(..., description='Идентификатор товара')
    amount: int = Field(..., ge=1, description='Количество')

class SProductShort(BaseModel):
    product_id: int = Field(..., description='Идентификатор товара')
    title: str = Field(..., description='Наименование')
    amount: int = Field(..., ge=1, description='Количество')

class SFullOrder(SOrder):
    products: list[SProductShort] = Field(..., description='Товары')

