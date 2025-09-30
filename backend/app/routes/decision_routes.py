from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import uuid
from app.services.chat_storage import chat_storage
from app.services.ai_service import ai_service

router = APIRouter()

class ChatMessage(BaseModel):
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    session_id: str
    total_messages: int

@router.post("/chat", response_model=ChatResponse)
async def chat_with_assistant(chat_message: ChatMessage):
    """处理聊天消息并返回 AI 响应"""
    try:
        # 获取或创建 session_id
        session_id = chat_message.session_id or str(uuid.uuid4())
        
        # 保存用户消息
        chat_storage.add_message(
            session_id=session_id,
            role="user",
            content=chat_message.message
        )
        
        # 获取历史消息作为上下文
        session_data = chat_storage.get_session(session_id)
        context = session_data.get("messages", []) if session_data else []
        
        # 获取 AI 回复（使用真正的 AI 服务）
        ai_response = ai_service.get_response(chat_message.message, context)
        
        # 保存 AI 回复
        chat_storage.add_message(
            session_id=session_id,
            role="assistant",
            content=ai_response
        )
        
        # 获取更新后的消息总数
        updated_session = chat_storage.get_session(session_id)
        total_messages = len(updated_session.get("messages", []))
        
        return ChatResponse(
            response=ai_response,
            session_id=session_id,
            total_messages=total_messages
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sessions")
async def get_all_sessions():
    """获取所有会话列表"""
    return chat_storage.get_all_sessions()

@router.get("/session/{session_id}")
async def get_session_history(session_id: str):
    """获取特定会话的历史记录"""
    session_data = chat_storage.get_session(session_id)
    if not session_data:
        raise HTTPException(status_code=404, detail="Session not found")
    return session_data
