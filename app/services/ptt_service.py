import requests
from bs4 import BeautifulSoup


PTT_RENT_URL = "https://www.ptt.cc/bbs/rent-exp/index.html"


def fetch_ptt_rent_posts(limit: int = 5) -> list[dict]:
    """取得 PTT rent-exp 板目前首頁中可讀取的文章。"""
    response = requests.get(
        PTT_RENT_URL,
        headers={"User-Agent": "Mozilla/5.0"},
        cookies={"over18": "1"},
        timeout=10,
    )
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    posts = []
    for article in soup.select("div.r-ent"):
        link = article.select_one("div.title a")
        author = article.select_one("div.author")

        # 已刪除文章沒有連結，不能提供給使用者開啟。
        if not link:
            continue

        posts.append({
            "title": link.get_text(strip=True),
            "link": f"https://www.ptt.cc{link['href']}",
            "author": author.get_text(strip=True) if author else "未知作者",
        })
        if len(posts) >= limit:
            break

    return posts
