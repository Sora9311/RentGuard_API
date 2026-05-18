from fastapi import APIRouter
from app.schemas.scenarios import ScenarioAdviceRequest, ScenarioAdviceResponse
from app.services.scenario_service import generate_scenario_advice

router = APIRouter()

@router.get("/categories")
async def get_scenario_categories():
    """
    取得所有預設的租屋糾紛情境分類，供前端選單使用。
    """
    # ⚠️ [標註需求：前端 UI]
    # 這裡的分類可以與前端討論後寫死，或是未來開一個資料表來維護。
    return {
        "categories": [
            {"id": "deposit", "name": "押金扣留"},
            {"id": "repair", "name": "修繕責任"},
            {"id": "early_termination", "name": "提前解約"},
            {"id": "noise", "name": "鄰居噪音"}
        ]
    }

@router.post("/advice", response_model=ScenarioAdviceResponse)
async def get_scenario_advice(request: ScenarioAdviceRequest):
    """
    根據使用者選定的情境與細節，回傳 AI 生成的應對步驟。
    """
    result = generate_scenario_advice(
        category=request.category, 
        details=request.details
    )
    
    return ScenarioAdviceResponse(**result)