from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # --- 專案基本資訊 ---
    PROJECT_NAME: str = "RentGuard AI 租屋專家知識庫 API"
    VERSION: str = "0.1.0"

    # --- API 金鑰設定 (會自動優先從 .env 讀取真實數值) ---
    OPENAI_API_KEY: str = ""
    PINECONE_API_KEY: str = ""
    GEMINI_API_KEY: str = ""

    # --- LLM 模型設定 ---
    # 預設改為使用 Gemini (如同我們之前討論的，速度快且有免費額度)
    LLM_MODEL: str = "gemini-1.5-flash"

    # --- Embedding (文字轉向量) 設定 ---
    # 預設改為 huggingface (本機免費執行)，避免消耗 OpenAI 額度
    EMBEDDING_MODE: str = "huggingface"
    HF_EMBEDDING_MODEL: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"

    # --- 向量資料庫設定 ---
    VECTORSTORE_TYPE: str = "chroma"
    CHROMA_PERSIST_DIR: str = "./data/vectorstore"
    CHROMA_COLLECTION_NAME: str = "rental_law_docs"

    # --- 文件切割設定 ---
    CHUNK_SIZE: int = 500        # 每個 chunk 的最大字元數
    CHUNK_OVERLAP: int = 50      # 相鄰 chunk 之間的重疊字元數（保留上下文）

    # --- 檢索設定 ---
    RETRIEVER_TOP_K: int = 4     # 每次檢索取前 4 筆最相關的法條

    # --- 資料來源路徑 ---
    DATA_DIR: str = "./data/raw"

    # 設定要讀取的環境變數檔案
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

# 實例化設定物件，供其他模組直接 import
settings = Settings()