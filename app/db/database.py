# 檔案位置：app/db/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# 設定 SQLite 資料庫檔案的位置 (會建立在專案根目錄下的 rentguard.db)
SQLALCHEMY_DATABASE_URL = "sqlite:///./rentguard.db"

# 建立資料庫引擎 (connect_args 是專門為了 SQLite 與 FastAPI 搭配時所需的設定)
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# 建立 Session 工廠，用來產生與資料庫對話的 Session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 建立所有資料表模型的基礎類別 (Base Class)
Base = declarative_base()

# 建立一個依賴注入函數 (Dependency)，確保每次 API 請求結束後都會自動關閉資料庫連線
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()