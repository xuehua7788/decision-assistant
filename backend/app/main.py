from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Decision Assistant API")

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # 本地开发
        "https://decision-assistant-6a9f3h29e-bruces-projects-409b2d51.vercel.app",  # Vercel 生产环境
        "https://*.vercel.app",  # 其他 Vercel 预览部署
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 导入并注册路由
from app.routes import decision_routes
from app.services.chat_storage import chat_storage
from app.services.ai_service import ai_service

app.include_router(decision_routes.router, prefix="/api/decisions", tags=["decisions"])
print("✓ AI-powered decision routes loaded successfully")
print(f"✓ Chat storage initialized at: {chat_storage.storage_dir}")
print(f"✓ AI service ready: DeepSeek API")

@app.get("/")
async def root():
    return {"message": "Decision Assistant API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "backend", "ai": "DeepSeek"}

@app.get("/api/test")
async def test_endpoint():
    return {"message": "Test endpoint working"}
