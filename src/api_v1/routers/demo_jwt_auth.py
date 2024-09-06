import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from src.api_v1.cruds.user_crud import create_user
from src.api_v1.dependencies.security_dependencies import validate_auth_user
from src.api_v1.schemas.token_schemas import TokenInfo
from src.api_v1.schemas.user_schemas import UserSchema, UserOut
from src.auth.utils import encode_jwt
from src.core.database.db_helper import db_helper
from src.core.database.models import User

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", response_model=TokenInfo)
async def login(
    user: UserSchema = Depends(validate_auth_user),
) -> TokenInfo:
    """
    Роутер для аутентификации юзера по логину и паролю
    :param user:
    :return: JWT token
    """
    jwt_payload = {  # Сюда передаем то что хотим закодировать в токен
        "sub": user.id,
        "username": user.username,
        "email": user.email,
        # "logged_in_at": datetime.datetime.now().isoformat(),
    }
    token = encode_jwt(jwt_payload)
    return TokenInfo(
        access_token=token,
        token_type="Bearer",  # При использовании JWT применяем тип Bearer
    )


@router.post(
    "/register",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
)
async def register_user(
    user_in: UserSchema,
    session: AsyncSession = Depends(db_helper.get_db),
) -> User:
    return await create_user(session=session, user_in=user_in)
