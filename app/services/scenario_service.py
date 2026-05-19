from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from app.core.config import settings
import json
from app.core.exceptions import RentGuardException

llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    google_api_key=settings.GEMINI_API_KEY,
    temperature=0.3
)

def generate_scenario_advice(category: str, details: str) -> dict:
    """
    根據使用者選擇的糾紛情境，生成具體的解決步驟。
    """
    prompt_template = PromptTemplate.from_template(
        "你是一個專業的台灣租屋糾紛調解顧問。\n"
        "使用者遇到以下租屋問題：\n"
        "情境分類：{category}\n"
        "詳細狀況：{details}\n\n"
        "請給出具體的應對步驟，並務必以嚴格的 JSON 格式回傳，格式如下：\n"
        "{{\n"
        "  \"scenario_summary\": \"一句話總結目前狀況\",\n"
        "  \"advice_steps\": [\n"
        "    {{\"step_number\": 1, \"action\": \"第一步該做什麼\", \"description\": \"詳細說明\"}}\n"
        "  ],\n"
        "  \"relevant_laws\": [\"相關法規一\", \"相關法規二\"]\n"
        "}}\n\n"
        "JSON 回傳："
    )

    chain = prompt_template | llm

    try:
        response = chain.invoke({"category": category, "details": details})
        clean_json_str = response.content.replace("```json", "").replace("```", "").strip()
        return json.loads(clean_json_str)
    except Exception as e:
        
        raise RentGuardException(
            status_code=500, 
            message=f"生成情境建議時發生錯誤，請稍後再試。(錯誤細節: {str(e)})"
        )