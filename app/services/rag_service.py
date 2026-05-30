from typing import Dict, Any, List

# 1.換成 Google GenAI
# from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI

from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

# 2. 【修改】設定檔路徑改為對應你的 app.core.config
from app.core.config import settings

SYSTEM_PROMPT = """你是一位專業的台灣租屋法律助理。
根據下方提供的法律條文，用白話文解釋並給予行動建議。
若找不到相關資料，請回答：建議尋求正式法律諮詢，例如法律扶助基金會（412-8518）。

法律條文：
{context}

回答格式：
**📋 法條解釋（白話文）**
**💡 行動建議**
**⚠️ 注意事項**
**📌 免責聲明** 本回答僅供參考，不構成正式法律建議。
"""

PROMPT_TEMPLATE = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("human", "{input}"),
])

class RAGService:
    def __init__(self, retriever):
        self.retriever = retriever
        
        # 3. 【修改】將 ChatOpenAI 替換為 ChatGoogleGenerativeAI
        self.llm = ChatGoogleGenerativeAI(
            model=settings.LLM_MODEL,
            temperature=0,
            google_api_key=settings.GEMINI_API_KEY, # 對應你 config 裡的變數
        )
        
        def format_docs(docs):
            return "\n\n".join(doc.page_content for doc in docs)
        self.format_docs = format_docs
        self.rag_chain = (
            {
                "context": self.retriever | self.format_docs,
                "input": RunnablePassthrough(),
            }
            | PROMPT_TEMPLATE
            | self.llm
            | StrOutputParser()
        )
        print("[RAG Chain] 初始化完成，系統就緒！")

    def query(self, question: str) -> Dict[str, Any]:
        print(f"[查詢] 收到問題：{question}")
        answer = self.rag_chain.invoke(question)
        source_docs = self.retriever.invoke(question)
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