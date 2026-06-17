from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

import app.core.state as state
from app.core.security import get_current_user, require_admin
from app.schemas.users import CurrentUser
from app.schemas.chat import (
    MessageRequest,
    MessageResponse,
    StreamRequest,
    HistoryResponse,
    ChatMessage,
    ModelSwitchRequest,
    ModelInfoResponse,
)
from app.services.ollama_client import get_reply, stream_reply, list_available_models
from app.services.session_store import get_history, clear_history

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/message", response_model=MessageResponse)
async def send_message(body: MessageRequest, user: CurrentUser = Depends(get_current_user)):
    try:
        reply = await get_reply(user.id, body.session_id, body.message)
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Model unavailable: {str(e)}")
    return MessageResponse(reply=reply, session_id=body.session_id)


@router.post("/stream")
async def stream_message(body: StreamRequest, user: CurrentUser = Depends(get_current_user)):
    async def generator():
        try:
            async for chunk in stream_reply(user.id, body.session_id, body.message):
                yield chunk
        except Exception as e:
            import json
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
            yield "data: [DONE]\n\n"

    return StreamingResponse(generator(), media_type="text/event-stream")


@router.get("/history/{session_id}", response_model=HistoryResponse)
async def get_chat_history(session_id: str, user: CurrentUser = Depends(get_current_user)):
    messages = await get_history(user.id, session_id)
    return HistoryResponse(
        session_id=session_id,
        messages=[ChatMessage(**m) for m in messages],
    )


@router.delete("/history/{session_id}")
async def delete_chat_history(session_id: str, user: CurrentUser = Depends(get_current_user)):
    await clear_history(user.id, session_id)
    return {"status": "cleared", "session_id": session_id}


@router.get("/model", response_model=ModelInfoResponse)
async def get_model(user: CurrentUser = Depends(get_current_user)):
    available = await list_available_models()
    return ModelInfoResponse(active_model=state.active_model, available_models=available)


@router.post("/model", response_model=ModelInfoResponse)
async def switch_model(body: ModelSwitchRequest, user: CurrentUser = Depends(get_current_user)):
    require_admin(user)
    available = await list_available_models()
    if body.model not in available:
        raise HTTPException(
            status_code=400,
            detail=f"Model '{body.model}' not found. Available: {available}",
        )
    state.active_model = body.model
    return ModelInfoResponse(active_model=state.active_model, available_models=available)
