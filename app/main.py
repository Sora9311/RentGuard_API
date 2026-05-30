from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings  
from app.api import chat, contracts, scenarios, news  # 整理重複的 import
from app.core.exceptions import RentGuardException, rentguard_exception_handler

# 引入資料庫引擎與模型
from app.db.database import engine, Base
from app.models import chat as chat_model 

# 引入 RAG 知識庫與大腦初始化工具
from app.db.vectorstore import get_embeddings, load_vectorstore, get_retriever
from app.services.rag_service import init_rag_service

# 指示SQLAlchemy在啟動時根據模型建立所有資料表
Base.metadata.create_all(bind=engine)

# 設定 FastAPI 的生命週期管理（開機時自動初始化 RAG）
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("⏳ [Lifespan] 啟動中：正在載入 RAG 知識庫與 AI 模型...")
    try:
        # 依序執行：初始化 Embedding -> 載入 Chroma 向量庫 -> 建立檢索器 -> 注入 RAG 服務
        embeddings = get_embeddings()
        vectorstore = load_vectorstore(embeddings)
        retriever = get_retriever(vectorstore)
        init_rag_service(retriever)
        print("✅ [Lifespan] RAG 知識庫與大腦載入成功，服務就緒！")
    except Exception as e:
        print(f"❌ [Lifespan] RAG 知識庫載入失敗，請檢查 data/vectorstore 檔案是否正確：{e}")
    
    yield  # 這裡交棒給 FastAPI 開始接收網路請求
    
    print("🛑 [Lifespan] 伺服器正在關閉...")

# 使用 settings 裡面的變數來初始化 FastAPI，並綁定 lifespan
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="提供租屋法律諮詢、合約分析與情境建議的後端服務",
    lifespan=lifespan  # 🆕 注入生命週期控制
)

# 先設定為 ["*"] 允許所有來源連線。之後改成前端的網址
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # 允許發出請求的網域
    allow_credentials=False,       # 是否允許攜帶Cookie或認證資訊
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