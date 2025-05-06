from pydantic import BaseModel, EmailStr, Field

from app.auth.models import Role


class SUserRegister(BaseModel):
    email: EmailStr = Field(..., description="Электронная почта")
    name: str = Field(..., min_length=3, max_length=50, description="Имя, от 3 до 50 символов")
    surname: str = Field(..., min_length=3, max_length=50, description="Фамилия, от 3 до 50 символов")
    patronymic: str | None = Field(..., min_length=3, max_length=50, description="Отчество, от 3 до 50 символов")
    password: str = Field(..., min_length=5, max_length=50, description="Пароль, от 5 до 50 знаков")
    role: Role = Field(..., description="Роль пользователя в системе")


class SUserLogin(BaseModel):
    email: EmailStr = Field(..., description="Электронная почта")
    password: str = Field(..., min_length=5, max_length=50, description="Пароль, от 5 до 50 знаков")


class SUserResponse(BaseModel):
    email: EmailStr = Field(..., description="Электронная почта")
    name: str = Field(..., min_length=3, max_length=50, description="Имя, от 3 до 50 символов")
    surname: str = Field(..., min_length=3, max_length=50, description="Фамилия, от 3 до 50 символов")
    patronymic: str | None = Field(..., min_length=3, max_length=50, description="Отчество, от 3 до 50 символов")
    role: Role = Field(..., description="Роль пользователя в системе")


class SLoginResponse(BaseModel):
    access_token: str = Field(..., description='JWT токен доступа')