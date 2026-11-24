from typing import Dict, Any, List

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from app.core.config import settings

# 💡 升級版顧問人設：解決評審說「只會丟法條、沒有解決問題」的痛點
SYSTEM_PROMPT = """你現在是一位專業且溫暖的台灣租屋法律顧問。你的任務不是死板背誦法條，而是幫助租客解決真實的租屋糾紛。

請根據下方提供的【參考法律資料】進行回覆。

【對話與回覆原則】：
1. 同理與釐清：若使用者的問題描述不夠完整（例如未說明合約有無特別約定、是否為定期租約等），先表達理解，並主動提出 1~2 個最關鍵的問題引導釐清，切勿在資訊不足時武斷下定論。
2. 具體行動建議：告知使用者目前具體可採取的實務步驟（例如：以 LINE/簡訊留存對話紀錄、寄發存證信函催告、向在地消保官申請調解）。
3. 白話解釋與標示來源：將法律概念轉為一般人聽得懂的白話文。引用時請說明「依據系統檢索到的規範...」，並將精確的法條內容整理在回答最末尾。
4. 免責與轉介：若參考資料完全不足以回答該問題，請誠實告知，並建議尋求崔媽媽基金會或法律扶助基金會（412-8518）協助。本回答僅供參考，不構成正式法律建議。

【參考法律資料】：
{context}
"""

PROMPT_TEMPLATE = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("human", "{input}"),
])

class RAGService:
    def __init__(self, retriever):
        self.retriever = retriever
        
        # 初始化 Gemini LLM
        self.llm = ChatGoogleGenerativeAI(
            model=settings.LLM_MODEL,
            temperature=0,
            google_api_key=settings.GEMINI_API_KEY, 
        )
        
        def format_docs(docs):
            return "\n\n".join(doc.page_content for doc in docs)
        self.format_docs = format_docs
        
        print("[RAG Service] 初始化完成，系統就緒！")

    def query(self, question: str) -> Dict[str, Any]:
        print(f"[查詢] 收到問題：{question}")
        
        # 🚀 修正 1：單次檢索 (移除原本重複呼叫的 retriever.invoke)
        source_docs = self.retriever.invoke(question)
        context = self.format_docs(source_docs)
        
        # 🚀 修正 2：生成回答並提取純文字 (.content)
        ai_message = self.llm.invoke(
            PROMPT_TEMPLATE.format_messages(
                context=context,
                input=question,
            )
        )
        answer = ai_message.content 
        
        # 整理來源文獻
        source_documents = self._format_source_documents(source_docs)
        print(f"[查詢] 完成，參考 {len(source_documents)} 筆法條")
        
        return {
            "answer": answer,
            "source_documents": source_documents,
        }

    def _format_source_documents(self, docs: List[Document]) -> List[Dict[str, str]]:
        formatted = []
        seen_sources = set()
        for doc in docs:
            source = doc.metadata.get("source", "未知來源")
            if source in seen_sources:
                continue
            seen_sources.add(source)
            formatted.append({
                "source": source,
                "category": doc.metadata.get("category", ""),
                "content": doc.page_content,
            })
        return formatted

_rag_service_instance: RAGService = None

def get_rag_service() -> RAGService:
    global _rag_service_instance
    if _rag_service_instance is None:
        raise RuntimeError("RAG 服務尚未初始化！")
    return _rag_service_instance

def init_rag_service(retriever) -> RAGService:
    global _rag_service_instance
    _rag_service_instance = RAGService(retriever)
    return _rag_service_instance