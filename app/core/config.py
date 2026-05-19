from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # 專案基本資訊
    PROJECT_NAME: str = "RentGuard AI 租屋專家知識庫 API"
    VERSION: str = "0.1.0"
    
    # API金鑰設定
    OPENAI_API_KEY: str = ""
    PINECONE_API_KEY: str = ""
    GEMINI_API_KEY: str = ""

    # 設定要讀取的環境變數檔案
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

# 實例化設定物件，供其他模組直接import
settings = Settings()