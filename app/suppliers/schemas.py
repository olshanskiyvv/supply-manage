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

class SSupplierProductRB(BaseModel):
    product_id: int = Field(..., description="Идентификатор товары")
    supplier_product_code: str = Field(..., description="Код товара у поставщика")
    current_price: int = Field(..., description="Текущая цена")

class SProductShort(BaseModel):
    product_id: int = Field(..., description="Идентификатор товара")
    title: str = Field(..., description="Наименование товара")
    product_code: str = Field(..., description="Код товара у поставщика")
    price: int = Field(..., description="Цена")

class SFullSupplier(SSupplier):
    products: list[SProductShort] = Field(..., description="Поставляемые товары")

