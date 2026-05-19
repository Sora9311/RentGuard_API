import feedparser

def fetch_rental_news(limit: int = 5) -> list:
    """
    透過 Google News RSS 抓取台灣租屋相關新聞
    """
    # Google News RSS搜尋網址(設定關鍵字：台灣 租屋，語言：繁體中文)
    rss_url = "https://news.google.com/rss/search?q=台灣+租屋&hl=zh-TW&gl=TW&ceid=TW:zh-Hant"
    
    # feedparser讀取網址
    feed = feedparser.parse(rss_url)
    
    news_list = []
    # 只取前limit筆新聞(預設5筆)
    for entry in feed.entries[:limit]:
        news_list.append({
            "title": entry.title,
            "link": entry.link,
            "published_at": entry.published,
            "source": entry.source.title if 'source' in entry else "Google News"
        })
        
    return news_list