# 檔案位置：app/models/chat.py
from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from app.db.database import Base

class ChatHistory(Base):
    __tablename__ = "chat_histories"  # 資料表名稱

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True, nullable=False) # 辨識是哪一次的對話
    role = Column(String, nullable=False)                   # 紀錄是'user'還是 'ai'
    content = Column(Text, nullable=False)                  # 具體的對話內容
    created_at = Column(DateTime, default=datetime.utcnow)  # 對話發生的時間