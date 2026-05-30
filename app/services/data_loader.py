# ========================================
# app/data_loader.py - 資料載入與切割模組
# ========================================
# 負責：
#   1. 讀取 JSON / TXT 格式的法律文本
#   2. 使用 LangChain TextSplitter 進行 Chunking
#   3. 回傳帶有 metadata（來源、分類）的 Document 列表

import json
import os
from pathlib import Path
from typing import List

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.core.config import settings

def load_json_documents(file_path: str) -> List[Document]:
    """
    讀取 JSON 格式的法律文件。
    
    預期 JSON 格式：
    [
        {
            "source": "民法第421條",
            "category": "租賃定義",
            "content": "法條內容..."
        },
        ...
    ]
    
    Args:
        file_path: JSON 檔案路徑
        
    Returns:
        List[Document]: LangChain Document 物件列表，包含 page_content 與 metadata
    """
    documents = []
    
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    for item in data:
        # 將每筆法條轉為 LangChain Document 格式
        # metadata 會在後續檢索時作為來源引用的依據
        doc = Document(
            page_content=item.get("content", ""),
            metadata={
                "source": item.get("source", "未知來源"),
                "category": item.get("category", "未分類"),
                "file": os.path.basename(file_path),
            }
        )
        documents.append(doc)
    
    print(f"[資料載入] 從 {file_path} 載入 {len(documents)} 筆法條")
    return documents


def load_txt_documents(file_path: str) -> List[Document]:
    """
    讀取純文字格式的法律文件。
    適用於從全國法規資料庫直接下載的 .txt 檔案。
    
    Args:
        file_path: TXT 檔案路徑
        
    Returns:
        List[Document]: 單一 Document 物件（整份文件），後續會再切割
    """
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    doc = Document(
        page_content=content,
        metadata={
            "source": os.path.basename(file_path),
            "category": "法律全文",
            "file": os.path.basename(file_path),
        }
    )
    
    print(f"[資料載入] 從 {file_path} 載入文字文件（{len(content)} 字元）")
    return [doc]


def load_all_documents(data_dir: str = None) -> List[Document]:
    """
    掃描資料資料夾，自動載入所有 .json 與 .txt 檔案。
    
    Args:
        data_dir: 資料夾路徑（預設使用 settings.DATA_DIR）
        
    Returns:
        List[Document]: 所有文件合併後的列表
    """
    data_dir = data_dir or settings.DATA_DIR
    all_documents = []
    
    data_path = Path(data_dir)
    if not data_path.exists():
        raise FileNotFoundError(f"資料目錄不存在：{data_dir}")
    
    # 依副檔名分派給對應的載入函式
    for file_path in data_path.iterdir():
        if file_path.suffix == ".json":
            docs = load_json_documents(str(file_path))
            all_documents.extend(docs)
        elif file_path.suffix == ".txt":
            docs = load_txt_documents(str(file_path))
            all_documents.extend(docs)
    
    print(f"[資料載入] 共載入 {len(all_documents)} 筆原始文件")
    return all_documents


def split_documents(documents: List[Document]) -> List[Document]:
    """
    將文件進行 Chunking（切割成較小的片段），提升向量搜尋精準度。
    
    使用 RecursiveCharacterTextSplitter：
    - 優先在段落、句號、空白等自然邊界切割
    - 適合中文法律條文（比 CharacterTextSplitter 更聰明）
    
    Args:
        documents: 原始 Document 列表
        
    Returns:
        List[Document]: 切割後的 Document 列表（chunks）
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.CHUNK_SIZE,        # 每個 chunk 最多 500 字元
        chunk_overlap=settings.CHUNK_OVERLAP,  # 相鄰 chunk 重疊 50 字元，保留上下文
        # 中文切割優先順序：段落 > 句號/問號 > 逗號 > 空白 > 單字
        separators=["\n\n", "\n", "。", "；", "，", " ", ""],
        length_function=len,
    )
    
    chunks = splitter.split_documents(documents)
    print(f"[文件切割] {len(documents)} 筆原始文件 → {len(chunks)} 個 chunks")
    return chunks
