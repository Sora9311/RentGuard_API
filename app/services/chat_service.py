from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from app.core.config import settings
from sqlalchemy.orm import Session
from app.models.chat import ChatHistory

llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    google_api_key=settings.GEMINI_API_KEY,
    temperature=0.2 
)

def generate_rentguard_response(query: str, session_id: str, db: Session) -> dict:
    
    # 🌟 1. 準備一個空字串來放對話紀錄
    chat_history_str = "無歷史紀錄。\n"

    if session_id:
        # 🌟 2. 從資料庫撈取這個 session_id 過去的對話 (為了避免字數爆掉，我們只拿最近的 10 筆)
        past_messages = db.query(ChatHistory).filter(
            ChatHistory.session_id == session_id
        ).order_by(ChatHistory.id.desc()).limit(10).all()
        
        # 因為 order_by desc 是從最新排到最舊，我們要把它反轉回來，讓時間順序正確
        past_messages.reverse()

        # 🌟 3. 如果有歷史紀錄，就把紀錄組成字串
        if past_messages:
            chat_history_str = ""
            for msg in past_messages:
                role_name = "房客" if msg.role == "user" else "RentGuard AI"
                chat_history_str += f"{role_name}：{msg.content}\n"

        # 儲存這次的問題
        user_message = ChatHistory(session_id=session_id, role="user", content=query)
        db.add(user_message)
        db.commit()

    # 🌟 4. 修改 Prompt，把 {chat_history} 塞進去讓 AI 參考
    prompt_template = PromptTemplate.from_template(
        "你是一個專業的台灣租屋法律顧問「RentGuard AI」。\n"
        "請以客觀、友善且具建設性的語氣，回答房客的問題。\n\n"
        "【歷史對話紀錄】\n"
        "{chat_history}\n\n"
        "【最新問題】\n"
        "房客：{query}\n"
        "RentGuard AI："
    )

    chain = prompt_template | llm

    try:
        # 🌟 5. 將歷史對話與最新問題一起傳給 Gemini
        response = chain.invoke({
            "query": query, 
            "chat_history": chat_history_str
        })
        answer = response.content
        sources = ["(尚未串接 RAG 知識庫，此為 Gemini 基礎生成)"]
        
        # 儲存 AI 的回答
        if session_id:
            ai_message = ChatHistory(session_id=session_id, role="ai", content=answer)
            db.add(ai_message)
            db.commit()

    except Exception as e:
        answer = f"系統發生錯誤，無法生成回覆。(錯誤訊息：{str(e)})"
        sources = []

    return {
        "answer": answer,
        "sources": sources
    }