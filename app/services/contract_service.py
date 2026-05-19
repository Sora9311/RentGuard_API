from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from app.core.config import settings
import json

llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    google_api_key=settings.GEMINI_API_KEY, 
    temperature=0.1
)

def analyze_contract_text(contract_text: str) -> dict:
    """
    接收合約文字，呼叫 LLM 進行條款風險分析，並要求回傳 JSON 格式。
    """
    # 要求LLM回傳JSON格式，方便解析
    prompt_template = PromptTemplate.from_template(
        "你是一個專業的台灣租屋合約審查律師。\n"
        "請分析以下租屋合約內容，揪出不合理、違法或對房客不利的條款。\n"
        "請務必以嚴格的 JSON 格式回傳，格式如下：\n"
        "{{\n"
        "  \"summary\": \"整體合約的簡短評價\",\n"
        "  \"risks\": [\n"
        "    {{\"clause\": \"原文段落\", \"risk_level\": \"高/中/低\", \"suggestion\": \"給房客的建議\"}}\n"
        "  ]\n"
        "}}\n\n"
        "合約內容：\n{contract_text}\n\n"
        "JSON 回傳："
    )

    chain = prompt_template | llm

    try:
        response = chain.invoke({"contract_text": contract_text})
        # 將LLM回傳的JSON字串解析成Python字典
        clean_json_str = response.content.replace("```json","").replace("```", "").strip()
        result_dict = json.loads(clean_json_str)
        return result_dict
    except Exception as e:
        # 錯誤處理
        return {
            "summary": f"分析過程發生錯誤：{str(e)}",
            "risks": []
        }