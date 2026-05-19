from pydantic import BaseModel, Field
from typing import List

# 若直接上傳 PDF 或圖片，API改為Multipart Form Data。
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