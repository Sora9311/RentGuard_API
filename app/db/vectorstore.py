# ========================================
# app/db/vectorstore.py - 向量化與向量資料庫模組
# ========================================
# 負責：
#   1. 初始化 Embedding 模型（Google Gemini API）
#   2. 建立向量資料庫（Chroma）
#   3. 提供向量資料庫的讀取與重建功能

from typing import List
from langchain_core.documents import Document
from langchain_core.vectorstores import VectorStoreRetriever

from app.core.config import settings

def get_embeddings():
    """
    使用 Google Gemini API 進行 Embedding。
    透過雲端處理，徹底解決 Render 免費主機記憶體不足 (OOM) 的問題。
    """
    from langchain_google_genai import GoogleGenerativeAIEmbeddings
    
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",
        google_api_key=settings.GEMINI_API_KEY
    )
    print(f"[Embedding] 已切換為雲端超輕量 Google 模型：text-embedding-004")
    
    return embeddings


def build_vectorstore(chunks: List[Document], embeddings):
    """將切割好的 Document chunks 向量化並建立向量資料庫 (Chroma)"""
    db_type = settings.VECTORSTORE_TYPE.lower()
    
    if db_type == "chroma":
        from langchain_community.vectorstores import Chroma
        
        vectorstore = Chroma.from_documents(
            documents=chunks,
            embedding=embeddings,
            persist_directory=settings.CHROMA_PERSIST_DIR,
            collection_name=settings.CHROMA_COLLECTION_NAME,
        )
        print(f"[向量資料庫] Chroma 建立完成，儲存於：{settings.CHROMA_PERSIST_DIR}")
        
    else:
        raise ValueError(f"請在 config 中將 VECTORSTORE_TYPE 設定為 'chroma'")
    
    return vectorstore


def load_vectorstore(embeddings):
    """載入已存在的 Chroma 向量資料庫"""
    db_type = settings.VECTORSTORE_TYPE.lower()
    
    if db_type == "chroma":
        from langchain_community.vectorstores import Chroma
        import os
        
        if not os.path.exists(settings.CHROMA_PERSIST_DIR):
            raise FileNotFoundError(
                f"找不到 Chroma 資料庫：{settings.CHROMA_PERSIST_DIR}\n"
                "請先執行重建資料庫的腳本！"
            )
        
        vectorstore = Chroma(
            persist_directory=settings.CHROMA_PERSIST_DIR,
            embedding_function=embeddings,
            collection_name=settings.CHROMA_COLLECTION_NAME,
        )
        # Chroma V0.4.x 的數量查詢方式
        try:
            count = vectorstore._collection.count()
            print(f"[向量資料庫] 已載入既有 Chroma 資料庫，文件數：{count}")
        except:
            print("[向量資料庫] 已載入既有 Chroma 資料庫。")
        return vectorstore
        
    else:
        raise ValueError("請使用 chroma 作為向量資料庫")


def get_retriever(vectorstore) -> VectorStoreRetriever:
    """從向量資料庫建立 Retriever"""
    retriever = vectorstore.as_retriever(
        search_type="similarity",          
        search_kwargs={"k": settings.RETRIEVER_TOP_K},  
    )
    print(f"[Retriever] 初始化完成，每次查詢返回 Top-{settings.RETRIEVER_TOP_K} 筆")
    return retriever