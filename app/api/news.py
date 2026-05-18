from fastapi import APIRouter, HTTPException
from app.schemas.news import NewsResponse
from app.services.news_service import fetch_rental_news

router = APIRouter()

@router.get("/", response_model=NewsResponse)
async def get_latest_news(limit: int = 5):
    """
    取得最新的台灣租屋相關新聞。
    - limit: 限制回傳的新聞數量 (預設為 5 篇)
    """
    try:
        articles = fetch_rental_news(limit=limit)
        return NewsResponse(
            status="success",
            total_results=len(articles),
            articles=articles
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"抓取新聞失敗：{str(e)}")