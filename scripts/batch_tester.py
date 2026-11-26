import csv
import time
import requests
from pathlib import Path

API_URL = "http://127.0.0.1:8000/api/v1/chat/query"
INPUT_CSV = Path("data/test_questions.csv")
OUTPUT_CSV = Path("data/test_results.csv")

def run_batch_test():
    if not INPUT_CSV.exists():
        print(f"找不到題庫檔案：{INPUT_CSV}")
        return

    results = []
    with open(INPUT_CSV, mode="r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        questions = list(reader)

    print(f"開始執行批次測試，共 {len(questions)} 題...")

    for row in questions:
        q_id = row["id"]
        category = row["category"]
        question = row["question"]
        expected = [k.strip() for k in row["expected_keywords"].split(";") if k.strip()]

        payload = {
            "query": question,
            "session_id": f"batch_eval_{q_id}"
        }

        start_time = time.time()
        try:
            resp = requests.post(API_URL, json=payload, timeout=30)
            elapsed = round(time.time() - start_time, 2)

            if resp.status_code == 200:
                data = resp.json()
                answer = data.get("answer", "")
                sources = [s.get("source", "") for s in data.get("source_documents", [])]
                
                # 簡易關鍵字命中檢查（輔助人工評估）
                hit_count = sum(1 for kw in expected if kw in answer)
                hit_status = f"{hit_count}/{len(expected)}"
                status = "SUCCESS"
            else:
                answer = f"HTTP {resp.status_code}: {resp.text}"
                sources = []
                hit_status = "0/0"
                status = "HTTP_ERROR"

        except Exception as e:
            elapsed = round(time.time() - start_time, 2)
            answer = str(e)
            sources = []
            hit_status = "0/0"
            status = "EXCEPTION"

        print(f"[第 {q_id} 題] 狀態: {status} | 耗時: {elapsed}s | 關鍵字命中: {hit_status} | 來源數: {len(sources)}")

        results.append({
            "id": q_id,
            "category": category,
            "question": question,
            "status": status,
            "response_time_sec": elapsed,
            "keyword_hit": hit_status,
            "sources_retrieved": " | ".join(sources),
            "ai_answer": answer,
        })

        # 避免觸發 Gemini API Rate Limit
        time.sleep(2)

    # 使用 utf-8-sig 編碼，確保 Excel 開啟中文不亂碼
    fieldnames = [
        "id", "category", "question", "status",
        "response_time_sec", "keyword_hit", "sources_retrieved", "ai_answer"
    ]
    with open(OUTPUT_CSV, mode="w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"\n測試完成！結果已匯出至：{OUTPUT_CSV}")

if __name__ == "__main__":
    run_batch_test()