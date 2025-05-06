from pydantic import BaseModel, Field

from app.products.models import MeasureUnit


class SProductFilters(BaseModel):
    title: str = Field('', description="Подстрока наименования")

class SProduct(BaseModel):
    id: int = Field(..., description='Идентификатор')
    title: str = Field(..., description='Наименование')
    description: str = Field(..., description='Описание')
    available: int = Field(..., description='Остаток на складе')
    unit: MeasureUnit = Field(..., description='Единица измерения')

class SSupplierShort(BaseModel):
    title: str = Field(..., description='Наименование')
    price: int = Field(..., ge=0, description='Цена')

class SFullProduct(SProduct):
    suppliers: list[SSupplierShort] = Field(default_factory=list, description='Доступные поставщики')

class SProductRB(BaseModel):
    title: str = Field(..., description='Наименование')
    description: str = Field(..., description='Описание')
    available: int = Field(..., description='Остаток на складе')
    unit: MeasureUnit = Field(..., description='Единица измерения')


