from pydantic import BaseModel, Field
from typing import Optional, List

# 定義前端送來的Request格式
class ChatRequest(BaseModel):
    query: str = Field(..., description="房客提問的租屋問題", example="房東可以隨便扣押金嗎？")
    session_id: Optional[str] = Field(None, description="對話的 Session ID，用於未來維持對話上下文")

# 定義回傳給前端的Response格式
class ChatResponse(BaseModel):
    answer: str = Field(..., description="AI 生成的專業回覆")
    sources: List[str] = Field(default=[], description="參考的法律條文或外部資料來源")