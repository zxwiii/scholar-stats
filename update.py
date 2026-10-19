import urllib.request
import json
import re
from datetime import datetime, timezone, timedelta

# Google Scholar ID
SCHOLAR_ID = "RzJmjLkAAAAJ"
URL = f"https://scholar.google.com/citations?user={SCHOLAR_ID}&hl=en"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def fetch_stats():
    req = urllib.request.Request(URL, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as resp:
        html = resp.read().decode("utf-8")

    # 匹配右侧引用统计表格中的数字
    # Google Scholar 表格格式一般为:
    # Citations: All, Since 20XX
    # h-index: All, Since 20XX
    # i10-index: All, Since 20XX
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
        raise ValueError(f"无法匹配到统计数据，HTML格式可能变更。提取到的内容: {matches}")

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

    # 保存为 scholar.json
    with open("scholar.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print("抓取成功！数据内容：", data)

if __name__ == "__main__":
    fetch_stats()
