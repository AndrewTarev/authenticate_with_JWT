from jwt.exceptions import InvalidTokenError
from fastapi import Depends, status, HTTPException, Form
from fastapi.security import (
    OAuth2PasswordBearer,
    HTTPAuthorizationCredentials,
    HTTPBearer,
)
from jwt import InvalidTokenError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api_v1.schemas.user_schemas import UserOut, UserSchema
from src.auth.utils import validate_password, decode_jwt
from src.core.database.db_helper import db_helper
from src.core.database.models import User

# oauth2_scheme = OAuth2PasswordBearer(
#     tokenUrl="/api/v1/login"
# )  # для получения логина и пароля при аутентификации

# http_bearer = HTTPBearer()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def validate_auth_user(
    # form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    username: str = Form(...),
    password: str = Form(...),
    session: AsyncSession = Depends(db_helper.get_db),
) -> UserOut:
    stmt = select(User).where(User.username == username)
    res = await session.execute(stmt)
    user = res.scalars().first()

    if not user or validate_password(password, user.password) is False:
        raise HTTPException(
            status_code=400,
            detail="Incorrect username or password",
        )

    if not user.active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User inactive",
        )

    return user


# HTTPAuthorizationCredentials — это класс, который используется для представления учетных данных, передаваемых в
# HTTP заголовке Authorization.
# 1. Атрибуты:
#    - scheme: Строка, которая представляет тип схемы авторизации, например, "Bearer", "Basic" и т. д.
#    - credentials: Строка, которая содержит учетные данные (например, токен или пароль).
#
# 2. Использование:
#    Обычно HTTPAuthorizationCredentials используется вместе с Depends, чтобы извлечь и проверить файл аутентификации из
# заголовка запроса.


def get_current_token_payload(
    # credentials: HTTPAuthorizationCredentials = Depends(http_bearer),
    token: str = Depends(oauth2_scheme),
):
    """
    Берем из заголовка Authorization JWT, декодируем и возвращаем полезную нагрузку
    # :param credentials: при работе с HTTPBearer мы в ручную копировали токен из роутера и вставляли в форму авторизации
    :param token: с помощью OAuth2PasswordBearer мы автоматически получам токен при аутентификации в форме запроса
    :return: Позволяет вытащить токен из заголовка Authorization
    """
    # token = credentials.credentials
    try:
        payload = decode_jwt(token=token)
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"invalid token error",
        )
    return payload


async def get_current_auth_user(
    payload: dict = Depends(get_current_token_payload),
    session: AsyncSession = Depends(db_helper.get_db),
):
    """
    Из полезной нагрузки получаем юзера из БД
    :param payload: полезная нагрузка
    :param session: сессия БД
    :return: Юзер
    """
    user_id: int = payload.get("sub")
    user = await session.get(User, user_id)
    if user:
        return user
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="token invalid (user not found)",
    )


def get_current_active_auth_user(
    user: UserSchema = Depends(get_current_auth_user),
):
    """
    Функция для проверки активен ли юзер
    :param user: юзер
    :return: активный юзер
    """
    if user.active:
        return user
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="inactive user",
    )