import csv
import sys
from collections import defaultdict
from pathlib import Path

def analyze(csv_path: str):
    path = Path(csv_path)
    if not path.exists():
        print(f"找不到檔案：{csv_path}")
        return

    total_q = 0
    success_q = 0
    total_time = 0.0
    total_kw_hit = 0
    total_kw_expected = 0
    exact_match_q = 0
    qa_source_hit_q = 0

    cat_stats = defaultdict(lambda: {"q": 0, "hit": 0, "exp": 0, "qa_hit": 0})

    with open(path, mode="r", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            total_q += 1
            cat = row["category"]
            cat_stats[cat]["q"] += 1

            if row["status"] == "SUCCESS":
                success_q += 1
                total_time += float(row["response_time_sec"])

                # 解析 keyword_hit (例如 "2/2")
                hit_str, exp_str = row["keyword_hit"].split("/")
                hit, exp = int(hit_str), int(exp_str)
                total_kw_hit += hit
                total_kw_expected += exp
                cat_stats[cat]["hit"] += hit
                cat_stats[cat]["exp"] += exp

                if exp > 0 and hit == exp:
                    exact_match_q += 1

                # 檢查是否撈到你餵進去的實務指南
                if "實務處理指南" in row["sources_retrieved"]:
                    qa_source_hit_q += 1
                    cat_stats[cat]["qa_hit"] += 1

    kw_rate = (total_kw_hit / total_kw_expected * 100) if total_kw_expected else 0
    exact_rate = (exact_match_q / success_q * 100) if success_q else 0
    qa_rate = (qa_source_hit_q / success_q * 100) if success_q else 0
    avg_time = (total_time / success_q) if success_q else 0

    print(f"=== 測試結果分析：{path.name} ===")
    print(f"總題數：{total_q} | 成功數：{success_q} | 平均耗時：{avg_time:.2f}s")
    print(f"1. 整體關鍵字命中率：{kw_rate:.1f}% ({total_kw_hit}/{total_kw_expected})")
    print(f"2. 完整命中題數比例：{exact_rate:.1f}% ({exact_match_q}/{success_q})")
    print(f"3. 實務指南檢索命中率：{qa_rate:.1f}% ({qa_source_hit_q}/{success_q})")
    print("\n--- 各分類表現 ---")
    for cat, s in cat_stats.items():
        c_kw = (s["hit"] / s["exp"] * 100) if s["exp"] else 0
        c_qa = (s["qa_hit"] / s["q"] * 100) if s["q"] else 0
        print(f"【{cat}】題數: {s['q']} | 關鍵字命中: {c_kw:.1f}% | 實務指南撈取: {c_qa:.1f}%")

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "data/test_results.csv"
    analyze(target)