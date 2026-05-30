import sys
import os

# 確保系統能從 scripts 資料夾往上找到 app 模組
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

# 1. 【修改】對齊你新的架構路徑
from app.services.data_loader import load_all_documents, split_documents
from app.db.vectorstore import build_vectorstore, get_embeddings
from app.core.config import settings

def main():
    s = settings

    print("=" * 50)
    print("  RentGuard AI - 向量資料庫建置工具")
    print("=" * 50)
    print(f"資料來源：{s.DATA_DIR}")

    print("[1/3] 載入法律文件...")
    documents = load_all_documents(s.DATA_DIR)
    if not documents:
        print("❌ 錯誤：data/raw/ 中沒有找到任何文件")
        sys.exit(1)
    print(f"    ✅ 載入 {len(documents)} 筆文件")

    print("[2/3] 切割文件 (Chunking)...")
    chunked_docs = split_documents(documents)
    print(f"    ✅ 切割完成，共 {len(chunked_docs)} 個 Chunk")

    # 2. 【修改】修正原本顯示 FAISS 的文字錯誤，改為 Chroma
    print("[3/3] 向量化並建立 Chroma 索引...")
    embeddings = get_embeddings()
    vectorstore = build_vectorstore(chunked_docs, embeddings)
    print(f"    ✅ 向量資料庫已儲存至 {s.CHROMA_PERSIST_DIR}")

    print()
    print("🎉 建置完成！現在可以啟動你的 FastAPI 服務了：")
    print("   uvicorn app.main:app --reload")

if __name__ == "__main__":
    main()