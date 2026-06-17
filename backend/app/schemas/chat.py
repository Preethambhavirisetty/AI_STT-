from typing import Literal
from pydantic import BaseModel, Field, field_validator


class MessageRequest(BaseModel):
    session_id: str = Field(min_length=1, max_length=128)
    message: str = Field(min_length=1, max_length=20000)

    @field_validator("message")
    @classmethod
    def message_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("message cannot be empty")
        return v.strip()


class StreamRequest(BaseModel):
    session_id: str = Field(min_length=1, max_length=128)
    message: str = Field(min_length=1, max_length=20000)

    @field_validator("message")
    @classmethod
    def message_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("message cannot be empty")
        return v.strip()


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class MessageResponse(BaseModel):
    reply: str
    session_id: str


class HistoryResponse(BaseModel):
    session_id: str
    messages: list[ChatMessage]


class ModelSwitchRequest(BaseModel):
    model: str = Field(min_length=1, max_length=200)


class ModelInfoResponse(BaseModel):
    active_model: str
    available_models: list[str]
