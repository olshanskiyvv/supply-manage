from pydantic import BaseModel, Field

class SSupplier(BaseModel):
    id: int = Field(..., description="Идентификатор")
    ogrn: str = Field(..., description="ОГРН")
    title: str = Field(..., description="Наименование")

class SSupplierAdmin(SSupplier):
    topic_name_base: str = Field(..., description="Базовое имя топиков Kafka")

class SSupplierRB(BaseModel):
    ogrn: str = Field(..., description="ОГРН")
    title: str = Field(..., description="Наименование")

class SSupplierFilters(BaseModel):
    title: str = Field('', description="Наименование")