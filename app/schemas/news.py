from pydantic import BaseModel
from typing import List

# 單篇新聞的格式
class NewsItem(BaseModel):
    title: str
    link: str
    published_at: str
    source: str

# API回傳的總格式
class NewsResponse(BaseModel):
    status: str
    total_results: int
    articles: List[NewsItem]