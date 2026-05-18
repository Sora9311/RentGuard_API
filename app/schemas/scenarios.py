from pydantic import BaseModel, Field
from typing import List, Optional

class ScenarioAdviceRequest(BaseModel):
    category: str = Field(..., description="情境分類，例如：'repair' (修繕), 'deposit' (押金)")
    details: str = Field(..., description="使用者補充的情境細節，例如：'冷氣壞了房東不修'")

class AdviceStep(BaseModel):
    step_number: int = Field(..., description="步驟序號")
    action: str = Field(..., description="具體該做什麼行動")
    description: str = Field(..., description="詳細說明與注意事項")

class ScenarioAdviceResponse(BaseModel):
    scenario_summary: str = Field(..., description="情境總結")
    advice_steps: List[AdviceStep] = Field(..., description="建議的應對步驟清單")
    relevant_laws: List[str] = Field(default=[], description="相關的法規參考")