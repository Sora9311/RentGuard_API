from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings  # 引入剛剛寫好的 settings
from app.api import chat, contracts, scenarios
from app.core.exceptions import RentGuardException, rentguard_exception_handler
from app.api import chat, contracts, scenarios, news  # 🌟 補上 news

# 🌟 新增這兩行：引入資料庫引擎與模型
from app.db.database import engine, Base
from app.models import chat as chat_model # 雖然檔名也是 chat，但為了跟 api 的 chat 區分，這裡取別名

# 🌟 新增這行：指示 SQLAlchemy 在啟動時根據模型建立所有資料表
Base.metadata.create_all(bind=engine)

# 使用 settings 裡面的變數來初始化 FastAPI
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="提供租屋法律諮詢、合約分析與情境建議的後端服務"
)
# 2. 設定 CORS 允許的來源網域
# 在開發階段，我先設定為 ["*"] 允許所有來源連線。
# 未來專案要正式上線時，記得把它改成前端真正的網址，例如 ["https://rentguard-ai.com"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # 允許發出請求的網域
    allow_credentials=True,       # 是否允許攜帶 Cookie 或認證資訊
    allow_methods=["*"],          # 允許的 HTTP 方法 (GET, POST, PUT, DELETE 等)
    allow_headers=["*"],          # 允許的 HTTP Headers
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
