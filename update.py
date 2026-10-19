import json
import re
from datetime import datetime, timezone, timedelta
from playwright.sync_api import sync_playwright

SCHOLAR_ID = "RzJmjLkAAAAJ"
URL = f"https://scholar.google.com/citations?user={SCHOLAR_ID}&hl=en"

def fetch_stats():
    with sync_playwright() as p:
        # 启动真实 Chromium 浏览器，完美绕过 403 反爬
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            locale="en-US"
        )
        page = context.new_page()
        page.goto(URL, wait_until="domcontentloaded", timeout=60000)
        
        # 等待引用表格渲染
        page.wait_for_selector("#gsc_rsb_st", timeout=15000)
        html = page.content()
        browser.close()

    # 提取引用数据
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
        raise ValueError(f"未能获取到数据，页面 HTML 片段: {html[:300]}")

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

    with open("scholar.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print("抓取成功！数据内容：", data)

if __name__ == "__main__":
    fetch_stats()
