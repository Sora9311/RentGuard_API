from fastapi import APIRouter, File, UploadFile, HTTPException
from app.services.contract_service import analyze_contract_text
import fitz  # PyMuPDF 的套件名稱

router = APIRouter()

@router.post("/upload")
async def analyze_contract_file(file: UploadFile = File(...)):
    """
    接收使用者上傳的 PDF 合約檔案，萃取文字後交由 Gemini 進行風險分析。
    """
    # 1. 檢查檔案格式是否為 PDF
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="目前只支援 PDF 檔案格式喔！")

    try:
        # 2. 讀取前端傳來的檔案二進位內容
        file_bytes = await file.read()
        
        # 3. 使用 PyMuPDF 將 PDF 轉換為純文字
        pdf_document = fitz.open(stream=file_bytes, filetype="pdf")
        extracted_text = ""
        
        for page_num in range(pdf_document.page_count):
            page = pdf_document.load_page(page_num)
            extracted_text += page.get_text()
            
        pdf_document.close()

        # 防呆機制：如果 PDF 全是圖片而沒有可選取的文字
        if not extracted_text.strip():
            raise HTTPException(
                status_code=400, 
                detail="無法從這份 PDF 中讀取到文字（可能為純圖片掃描檔，需額外掛載 OCR 模組）。"
            )

        # 4. 把萃取出來的合約文字，餵給我們之前寫好的 Gemini AI 服務
        result = analyze_contract_text(contract_text=extracted_text)
        
        return {
            "message": "檔案解析成功",
            "filename": file.filename,
            "analysis_result": result
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"檔案處理失敗：{str(e)}")