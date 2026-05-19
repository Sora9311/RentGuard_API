# 檔案位置：app/db/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# 設定SQLite資料庫檔案的位置
SQLALCHEMY_DATABASE_URL = "sqlite:///./rentguard.db"

# 建立資料庫引擎
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# 建立Session，用來產生與資料庫對話的Session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 建立所有資料表模型的基礎類別
Base = declarative_base()

# 確保每次API請求結束後都會自動關閉資料庫連線
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()