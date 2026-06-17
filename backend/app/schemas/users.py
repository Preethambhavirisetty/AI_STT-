from pydantic import BaseModel, Field


class CurrentUser(BaseModel):
    id: str
    name: str
    is_admin: bool = False
    created_at: str = ""


class CreateUserRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    api_key: str = Field(min_length=16, max_length=200)
    is_admin: bool = False


class UserResponse(BaseModel):
    id: str
    name: str
    is_admin: bool
    created_at: str


class UserListResponse(BaseModel):
    users: list[UserResponse]
    total: int
