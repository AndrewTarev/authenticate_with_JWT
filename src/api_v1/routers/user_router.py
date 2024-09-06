from fastapi import APIRouter, Depends

from src.api_v1.dependencies.security_dependencies import (
    get_current_active_auth_user,
    get_current_token_payload,
)
from src.api_v1.schemas.user_schemas import UserSchema, UserOut

router = APIRouter(tags=["Users"])


@router.get("/users/me/")
async def read_users_me(
    payload: dict = Depends(get_current_token_payload),
    user: UserSchema = Depends(get_current_active_auth_user),
):
    iat = payload.get("iat")
    return {
        "id": user.id,
        "email": user.email,
        "username": user.username,
        "logged_at_in": iat,
    }
