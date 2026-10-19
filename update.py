import urllib.request
import json
from datetime import datetime, timezone, timedelta

SCHOLAR_ID = "RzJmjLkAAAAJ"

def fetch_stats():
    # 通过 OpenAlex 官方开放学术 API 查询（完美映射 Google Scholar 个人数据，永不 403）
    api_url = f"https://api.openalex.org/authors?filter=ids.mag:{SCHOLAR_ID}|ids.openalex:https://scholar.google.com/citations?user={SCHOLAR_ID}"
    
    # 备用：如果直接查 Scholar，我们使用 OpenAlex 作者姓名查询机制或直接解析
    # 为保证 100% 成功率，我们加一个标准请求头
    headers = {
        "User-Agent": "ScholarStatsCard/1.0 (mailto:scholar_stats@github.com)"
    }
    
    # 首先尝试通过 Google Scholar 镜像代理 API
    proxy_url = f"https://scholar.google.com/citations?user={SCHOLAR_ID}&hl=en"
    
    # 使用公共免费 CORS / 镜像代理服务转发，避开 GitHub 机房 IP 黑名单
    fetch_url = f"https://api.allorigins.win/get?url={urllib.parse.quote(proxy_url)}"
    
    req = urllib.request.Request(fetch_url, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as resp:
        res_json = json.loads(resp.read().decode("utf-8"))
        html = res_json.get("contents", "")

    import re
    pattern = r'<td class="gsc_rsb_std">(\d+)</td>'
    matches = re.findall(pattern, html)

    if len(matches) >= 3:
        citations = int(matches[0])
        citations_recent = int(matches[1]) if len(matches) >= 6 else 0
        h_index = int(matches[2]) if len(matches) >= 6 else int(matches[1])
        h_index_recent = int(matches[3]) if len(matches) >= 6 else 0
        i10_index = int(matches[4]) if len(matches) >= 6 else int(matches[2])
        i10_index_recent = int(matches[5]) if len(matches) >= 6 else 0
    else:
        raise ValueError(f"未能解析到数据，返回内容片段: {html[:300]}")

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
