from fastapi import APIRouter, HTTPException, status, Response, Depends

from app.auth.dependencies import get_current_user, get_current_admin_user
from app.auth.models import User
from app.auth.service import authenticate_user
from app.schemas import SMessageResponse
from app.utils.jwt import get_password_hash, create_access_token
from app.auth.dao import UsersDAO
from app.auth.schemas import SUserRegister, SUserLogin, SUserResponse, SLoginResponse

router = APIRouter(prefix='/auth', tags=['Auth'])


@router.post("/register/")
async def register_user(user_data: SUserRegister) -> SMessageResponse:
    user = await UsersDAO.find_one_or_none(email=user_data.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='Пользователь уже существует'
        )
    user_dict = user_data.model_dump()
    user_dict['password'] = get_password_hash(user_data.password)
    await UsersDAO.add(**user_dict)
    return SMessageResponse(
        message='Вы успешно зарегистрированы!',
    )


@router.post("/login/")
async def auth_user(response: Response,
                    user_data: SUserLogin) -> SLoginResponse:
    check = await authenticate_user(email=user_data.email, password=user_data.password)
    if check is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Неверная почта или пароль')
    access_token = create_access_token({"sub": str(check.id)})
    response.set_cookie(key="users_access_token", value=access_token, httponly=True)
    return SLoginResponse(
        access_token=access_token,
    )

@router.get("/me/")
async def get_me(user_data: User = Depends(get_current_user)) -> SUserResponse:
    return SUserResponse.model_validate(user_data, from_attributes=True)

@router.post("/logout/")
async def logout_user(response: Response) -> SMessageResponse:
    response.delete_cookie(key="users_access_token")
    return SMessageResponse(
        message='Пользователь успешно вышел из системы',
    )

@router.get("/all_users/")
async def get_all_users(_: User = Depends(get_current_admin_user)):
    return await UsersDAO.find_all()