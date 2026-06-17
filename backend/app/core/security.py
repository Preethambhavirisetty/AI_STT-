from fastapi import Depends, Header, HTTPException, status

from app.core.config import settings
from app.schemas.users import CurrentUser
from app.services.users import get_user_by_api_key


async def get_current_user(x_api_key: str | None = Header(default=None)) -> CurrentUser:
    if not settings.REQUIRE_AUTH and not x_api_key:
        return CurrentUser(id="development", name="Development User", is_admin=True)

    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid API key",
        )

    user = await get_user_by_api_key(x_api_key)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid API key",
        )

    return CurrentUser(**user)


async def require_api_key(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
    return user


def require_admin(user: CurrentUser) -> None:
    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
