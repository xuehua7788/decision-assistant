from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.services.chat_storage import chat_storage
from app.services.ai_service import ai_service
from app.routes.auth_routes import router as auth_router

settings = get_settings()

app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    root_path=settings.api_root_path,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])

print(f"Chat storage initialized at: {chat_storage.storage_dir}")
print(f"Settings loaded. Max history messages: {settings.max_history_messages}")
print(
    "DeepSeek API key loaded."
    if settings.deepseek_api_key
    else "Warning: DeepSeek API key is not set."
)


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.post("/chat")
async def chat_endpoint(request: dict):
    session_id = request.get("session_id")
    user_message = request.get("message")

    if not session_id or not user_message:
        return {"error": "session_id and message are required fields"}

    chat_storage.add_message(session_id, "user", user_message)

    history = chat_storage.get_session(session_id)
    messages = history["messages"][-settings.max_history_messages :] if history else []

    response = await ai_service.generate_response(session_id, messages, user_message)

    chat_storage.add_message(session_id, "assistant", response)

    return {"response": response}


@app.get("/sessions")
async def list_sessions():
    return chat_storage.get_all_sessions()


@app.get("/sessions/{session_id}")
async def get_session(session_id: str):
    session = chat_storage.get_session(session_id)
    if session is None:
        return {"error": "Session not found"}
    return session


@app.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    deleted = chat_storage.delete_session(session_id)
    if not deleted:
        return {"error": "Session not found"}
    return {"status": "deleted"}


@app.get("/", summary="Service root", tags=["Health"])
async def read_root() -> dict[str, str]:
    return {"message": "Decision Assistant API"}
