from sqlalchemy.orm import Session
from langchain_core.messages import HumanMessage, AIMessage
from app.services.rag_service import get_rag_service
from app.models.chat import ChatHistory


def generate_rentguard_response(query: str, session_id: str, db: Session) -> dict:
    chat_history_msgs = []

    # --- 1. 先撈取歷史對話紀錄 (必須在存入最新問題之前撈，避免重複) ---
    if session_id:
        history_records = (
            db.query(ChatHistory)
            .filter(ChatHistory.session_id == session_id)
            .order_by(ChatHistory.id.asc())  # 依建立順序排列
            .all()
        )
        # 只取最近 10 筆避免 Token 過長，並轉為 LangChain 格式
        for record in history_records[-10:]:
            if record.role == "user":
                chat_history_msgs.append(HumanMessage(content=record.content))
            elif record.role == "ai":
                chat_history_msgs.append(AIMessage(content=record.content))

        # 存入使用者的最新問題
        user_message = ChatHistory(session_id=session_id, role="user", content=query)
        db.add(user_message)
        db.commit()

    # --- 2. 呼叫 RAG 大腦處理問題 (攜帶歷史記憶) ---
    try:
        rag = get_rag_service()
        result = rag.query(question=query, chat_history=chat_history_msgs)
        
        answer = result["answer"]
        # 直接保留完整的字典陣列，對應 SourceDocument Schema
        source_documents = result.get("source_documents", [])

        # --- 3. 儲存 AI 的回答 ---
        if session_id:
            ai_message = ChatHistory(session_id=session_id, role="ai", content=answer)
            db.add(ai_message)
            db.commit()

    except Exception as e:
        answer = f"系統發生錯誤，無法檢索知識庫與生成回覆。(錯誤訊息：{str(e)})"
        source_documents = []

    # --- 4. 回傳給 API Router ---
    return {
        "answer": answer,
        "source_documents": source_documents
    }