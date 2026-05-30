from app.services.rag_service import get_rag_service
from sqlalchemy.orm import Session
from app.models.chat import ChatHistory

def generate_rentguard_response(query: str, session_id: str, db: Session) -> dict:
    
    # --- 1. 儲存使用者的最新問題 ---
    if session_id:
        user_message = ChatHistory(session_id=session_id, role="user", content=query)
        db.add(user_message)
        db.commit()

    # --- 2. 呼叫 RAG 大腦處理問題 ---
    try:
        # 取得已經初始化好的 RAG 服務
        rag = get_rag_service()
        
        # 直接呼叫 query，自動完成「檢索法條 + 呼叫 Gemini」
        result = rag.query(query)
        
        # 拿到真正的回答與法條來源
        answer = result["answer"]
        
        # 🔧 這裡就是修復 500 錯誤的關鍵：將字典列表轉換為 Pydantic 要求的字串列表
        sources = [
            f"《{doc.get('source', '未知法規')}》: {doc.get('content', '')[:50]}..." 
            for doc in result["source_documents"]
        ]

        # --- 3. 儲存 AI 的回答 ---
        if session_id:
            ai_message = ChatHistory(session_id=session_id, role="ai", content=answer)
            db.add(ai_message)
            db.commit()

    except Exception as e:
        answer = f"系統發生錯誤，無法檢索知識庫與生成回覆。(錯誤訊息：{str(e)})"
        sources = []

    # --- 4. 回傳給前端 ---
    return {
        "answer": answer,
        "sources": sources
    }