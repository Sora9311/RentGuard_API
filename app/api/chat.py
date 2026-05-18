from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import generate_rentguard_response # 引入剛寫好的 Service
# 🌟 引入取得資料庫連線的函數
from app.db.database import get_db

router = APIRouter()

@router.post("/query", response_model=ChatResponse)
async def chat_with_rentguard(request: ChatRequest, db: Session = Depends(get_db)):
    """
    接收使用者的租屋問題，並透過 LangChain 回傳 AI 生成的解答。
    """
    
    # 將 Request 資料傳遞給 Service 層處理
    result = generate_rentguard_response(
        query=request.query, 
        session_id=request.session_id,
        db=db
    )
    
    # 將 Service 回傳的結果包裝成 Pydantic Schema 回傳給前端
    return ChatResponse(
        answer=result["answer"],
        sources=result["sources"]
    )