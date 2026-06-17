from fastapi import APIRouter, Depends

from app.core.security import get_current_user, require_admin
from app.schemas.users import CurrentUser, CreateUserRequest, UserListResponse, UserResponse
from app.services.users import create_user, list_users

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
async def me(user: CurrentUser = Depends(get_current_user)):
    return UserResponse(
        id=user.id,
        name=user.name,
        is_admin=user.is_admin,
        created_at=user.created_at,
    )


@router.get("", response_model=UserListResponse)
async def get_users(user: CurrentUser = Depends(get_current_user)):
    require_admin(user)
    users = await list_users()
    return UserListResponse(users=[UserResponse(**u) for u in users], total=len(users))


@router.post("", response_model=UserResponse)
async def post_user(body: CreateUserRequest, user: CurrentUser = Depends(get_current_user)):
    require_admin(user)
    created = await create_user(body.name, body.api_key, body.is_admin)
    return UserResponse(**created)
