# ========================================
# app/db/vectorstore.py - 向量化與向量資料庫模組
# ========================================
# 負責：
#   1. 初始化 Embedding 模型（HuggingFace）
#   2. 建立向量資料庫（Chroma）
#   3. 提供向量資料庫的讀取與重建功能

from typing import List
from langchain_core.documents import Document
from langchain_core.vectorstores import VectorStoreRetriever

# 1. 【修改】對齊你新的 config 路徑
from app.core.config import settings


def get_embeddings():
    """
    根據設定檔的 EMBEDDING_MODE，回傳對應的 Embedding 模型。
    預設使用 HuggingFace 本地模型。
    """
    mode = settings.EMBEDDING_MODE.lower()
    
    if mode == "huggingface":
        # ---- HuggingFace 本地 Embedding ----
        from langchain_community.embeddings import HuggingFaceEmbeddings
        
        embeddings = HuggingFaceEmbeddings(
            model_name=settings.HF_EMBEDDING_MODEL,
            model_kwargs={"device": "cpu"}, 
            encode_kwargs={"normalize_embeddings": True}, 
        )
        print(f"[Embedding] 使用 HuggingFace 模型：{settings.HF_EMBEDDING_MODEL}")
    
    else:
        # 如果不是 huggingface，拋出錯誤，避免誤用到需付費的 OpenAI
        raise ValueError(f"請在 .env 或 config.py 中將 EMBEDDING_MODE 設定為 'huggingface'")
    
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