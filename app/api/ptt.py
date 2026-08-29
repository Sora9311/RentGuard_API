from fastapi import APIRouter, HTTPException

from app.schemas.ptt import PttResponse
from app.services.ptt_service import fetch_ptt_rent_posts


router = APIRouter()


@router.get("/", response_model=PttResponse)
async def get_latest_ptt_posts(limit: int = 5):
    """取得 PTT rent-exp 板的最新文章。"""
    try:
        posts = fetch_ptt_rent_posts(limit=limit)
        return PttResponse(
            status="success",
            total_results=len(posts),
            posts=posts,
        )
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"抓取 PTT 文章失敗：{exc}") from exc
