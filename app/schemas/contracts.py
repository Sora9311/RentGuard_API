from pydantic import BaseModel, Field
from typing import List

# ⚠️ [標註需求：前端 UI]
# 請與前端確認：目前後端預期接收「純文字」格式的合約。
# 若前端希望直接上傳 PDF 或圖片，這裡的 API 設計必須改為 Multipart Form Data。
class ContractAnalyzeRequest(BaseModel):
    contract_text: str = Field(..., description="完整的租屋合約純文字內容")

# 定義單一風險條款的結構
class RiskItem(BaseModel):
    clause: str = Field(..., description="合約中的原文段落")
    risk_level: str = Field(..., description="風險等級，例如：高、中、低")
    suggestion: str = Field(..., description="給房客的具體建議或應對法規")

class ContractAnalyzeResponse(BaseModel):
    risks: List[RiskItem] = Field(..., description="分析出的潛在風險條款清單")
    summary: str = Field(..., description="整份合約的總體評價與簡短總結")