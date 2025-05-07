from pydantic import BaseModel, Field

class SMessageResponse(BaseModel):
    message: str = Field(..., description="Сообщение")


class SPaginationParams(BaseModel):
    page_num: int = Field(1, ge=1, description="Номер страницы с 1")
    page_size: int = Field(100, ge=10, description="Размер страницы с 10 до 100")

class SPageResponse[T](BaseModel):
    page: int = Field(1, ge=1, description="Номер страницы")
    size: int = Field(100, ge=10, description="Размер страницы")
    payload: list[T] = Field(..., description='Данные')