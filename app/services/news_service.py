import feedparser
import requests


GOOGLE_NEWS_URL = "https://news.google.com/rss/search"


def fetch_rental_news(limit: int = 5, keyword: str = "台灣 租屋") -> list[dict]:
    """取得 Google News 的台灣租屋相關新聞。"""
    response = requests.get(
        GOOGLE_NEWS_URL,
        params={
            "q": keyword,
            "hl": "zh-TW",
            "gl": "TW",
            "ceid": "TW:zh-Hant",
        },
        timeout=10,
    )
    response.raise_for_status()

    feed = feedparser.parse(response.content)
    news_list = []
    for entry in feed.entries[:limit]:
        source = entry.get("source")
        news_list.append({
            "title": entry.get("title", "無標題"),
            "link": entry.get("link", ""),
            "published_at": entry.get("published", ""),
            "source": source.get("title", "Google News") if source else "Google News",
        })

    return news_list
