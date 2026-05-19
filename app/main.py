from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings  # 引入settings
from app.api import chat, contracts, scenarios
from app.core.exceptions import RentGuardException, rentguard_exception_handler
from app.api import chat, contracts, scenarios, news  # news

# 引入資料庫引擎與模型
from app.db.database import engine, Base
from app.models import chat as chat_model # 區分api和chat 

# 指示SQLAlchemy在啟動時根據模型建立所有資料表
Base.metadata.create_all(bind=engine)

# 使用settings裡面的變數來初始化FastAPI
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="提供租屋法律諮詢、合約分析與情境建議的後端服務"
)
# 先設定為 ["*"] 允許所有來源連線。之後改成前端的網址
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # 允許發出請求的網域
    allow_credentials=True,       # 是否允許攜帶Cookie或認證資訊
    allow_methods=["*"],          # 允許的HTTP方法
    allow_headers=["*"],          # 允許的HTTP Headers
)

app.add_exception_handler(RentGuardException, rentguard_exception_handler)

@app.get("/health", tags=["System"])
def health_check():
    return {
        "status": "ok", 
        "message": f"{settings.PROJECT_NAME} Backend is running!"
    }

app.include_router(chat.router, prefix="/api/v1/chat", tags=["RAG Q&A"])
app.include_router(contracts.router, prefix="/api/v1/contracts", tags=["Contract Analysis"])
app.include_router(scenarios.router, prefix="/api/v1/scenarios", tags=["Scenario Advice"])
app.include_router(news.router, prefix="/api/v1/news", tags=["Rental News"])
