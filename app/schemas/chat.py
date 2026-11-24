from pydantic import BaseModel, Field
from typing import Optional, List

# 定義前端送來的Request格式
class ChatRequest(BaseModel):
    query: str = Field(..., description="房客提問的租屋問題", example="房東可以隨便扣押金嗎？")
    session_id: Optional[str] = Field(None, description="對話的 Session ID，用於未來維持對話上下文")

# 🚀 新增：定義來源資料的詳細結構
class SourceDocument(BaseModel):
    source: str = Field(..., description="資料來源名稱，如：民法第421條")
    category: str = Field(default="", description="資料分類")
    content: str = Field(..., description="具體的法條或文件內容")

# 定義回傳給前端的Response格式
class ChatResponse(BaseModel):
    answer: str = Field(..., description="AI 生成的專業回覆")
    source_documents: List[SourceDocument] = Field(default=[], description="參考的法律條文或外部資料來源的詳細內容")