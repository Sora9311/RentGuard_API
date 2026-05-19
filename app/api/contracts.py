from fastapi import APIRouter, File, UploadFile, HTTPException
from app.services.contract_service import analyze_contract_text
import fitz

router = APIRouter()

@router.post("/upload")
async def analyze_contract_file(file: UploadFile = File(...)):
    """
    接收使用者上傳的 PDF 合約檔案，萃取文字後交由 Gemini 進行風險分析。
    """
    # 檢查格式是否為PDF
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="目前只支援 PDF 檔案格式喔！")

    try:
        # 讀取前端傳來的檔案
        file_bytes = await file.read()
        
        # 使用PyMuPDF將PDF轉換為文字
        pdf_document = fitz.open(stream=file_bytes, filetype="pdf")
        extracted_text = ""
        
        for page_num in range(pdf_document.page_count):
            page = pdf_document.load_page(page_num)
            extracted_text += page.get_text()
            
        pdf_document.close()

        # 如果PDF全是圖片而沒有可選取的文字
        if not extracted_text.strip():
            raise HTTPException(
                status_code=400, 
                detail="無法從這份 PDF 中讀取到文字（可能為純圖片掃描檔，需額外掛載 OCR 模組）。"
            )

        # 把合約文字給AI
        result = analyze_contract_text(contract_text=extracted_text)
        
        return {
            "message": "檔案解析成功",
            "filename": file.filename,
            "analysis_result": result
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"檔案處理失敗：{str(e)}")