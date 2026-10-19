import json
import re
from datetime import datetime, timezone, timedelta
from curl_cffi import requests

SCHOLAR_ID = "RzJmjLkAAAAJ"
URL = f"https://scholar.google.com/citations?user={SCHOLAR_ID}&hl=en"

def fetch_stats():
    # 模拟真实 Chrome 浏览器指纹，完美解决 403 Forbidden
    response = requests.get(URL, impersonate="chrome120", timeout=30)
    
    if response.status_code != 200:
        raise ValueError(f"HTTP 请求失败，状态码: {response.status_code}")
        
    html = response.text

    # 提取总引用、h-index、i10-index
    pattern = r'<td class="gsc_rsb_std">(\d+)</td>'
    matches = re.findall(pattern, html)

    if len(matches) >= 6:
        citations = int(matches[0])
        citations_recent = int(matches[1])
        h_index = int(matches[2])
        h_index_recent = int(matches[3])
        i10_index = int(matches[4])
        i10_index_recent = int(matches[5])
    elif len(matches) >= 3:
        citations = int(matches[0])
        citations_recent = 0
        h_index = int(matches[1])
        h_index_recent = 0
        i10_index = int(matches[2])
        i10_index_recent = 0
    else:
        raise ValueError(f"无法匹配到统计数据，HTML 内容可能有变。")

    # 北京时间 (UTC+8)
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

    with open("scholar.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print("抓取成功！数据内容：", data)

if __name__ == "__main__":
    fetch_stats()
