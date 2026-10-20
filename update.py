import os
import json
import urllib.request
from datetime import datetime, timezone, timedelta

SCHOLAR_ID = "RzJmjLkAAAAJ"
API_KEY = os.environ.get("SERPAPI_KEY")

def fetch_stats():
    if not API_KEY:
        raise ValueError("未检测到环境变量 SERPAPI_KEY，请检查仓库 Secrets 配置！")

    # SerpApi 官方 Google Scholar Author API 接口
    api_url = f"https://serpapi.com/search.json?engine=google_scholar_author&author_id={SCHOLAR_ID}&api_key={API_KEY}&hl=en"

    print("正在通过 SerpApi 官方通道获取学术数据...")
    req = urllib.request.Request(api_url, headers={"User-Agent": "Mozilla/5.0"})
    
    with urllib.request.urlopen(req, timeout=20) as resp:
        result = json.loads(resp.read().decode("utf-8"))

    # 从返回的 JSON 中提取引用指标表格
    cited_by_table = result.get("cited_by", {}).get("table", [])
    
    citations = 0
    citations_recent = 0
    h_index = 0
    h_index_recent = 0
    i10_index = 0
    i10_index_recent = 0

    for row in cited_by_table:
        if "citations" in row:
            citations = int(row["citations"].get("all", 0))
            citations_recent = int(row["citations"].get("since_2021", 0) or row["citations"].get("since_2020", 0) or list(row["citations"].values())[1] if len(row["citations"]) > 1 else 0)
        elif "h_index" in row:
            h_index = int(row["h_index"].get("all", 0))
            h_index_recent = int(row["h_index"].get("since_2021", 0) or row["h_index"].get("since_2020", 0) or list(row["h_index"].values())[1] if len(row["h_index"]) > 1 else 0)
        elif "i10_index" in row:
            i10_index = int(row["i10_index"].get("all", 0))
            i10_index_recent = int(row["i10_index"].get("since_2021", 0) or row["i10_index"].get("since_2020", 0) or list(row["i10_index"].values())[1] if len(row["i10_index"]) > 1 else 0)

    # 获取北京时间 (UTC+8)
    bj_time = datetime.now(timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M")

    data = {
        "scholar_id": SCHOLAR_ID,
        "citations": citations,
        "citations_recent": citations_recent,
        "h_index": h_index,
        "h_index_recent": h_index_recent,
        "i10_index": i10_index,
        "i10_index_recent": i10_index_recent,
        "updated_at": bj_time
    }

    print("成功解析到最新学术数据：", data)

    # 写入文件
    with open("scholar.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    fetch_stats()
