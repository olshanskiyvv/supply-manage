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

class SProductRB(BaseModel):
    title: str = Field(..., description='Наименование')
    description: str = Field(..., description='Описание')
    available: int = Field(..., description='Остаток на складе')
    unit: MeasureUnit = Field(..., description='Единица измерения')


