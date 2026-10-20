import json
import re
import time
from datetime import datetime, timezone, timedelta
from playwright.sync_api import sync_playwright

SCHOLAR_ID = "RzJmjLkAAAAJ"
URL = f"https://scholar.google.com/citations?user={SCHOLAR_ID}&hl=en"

def fetch_stats():
    data = None
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-dev-shm-usage"
            ]
        )
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            locale="en-US"
        )
        
        # 预先注入已同意 Google 隐私政策的 Cookie，杜绝所有 Consent 弹窗和拦截
        context.add_cookies([
            {"name": "CONSENT", "value": "YES+cb.20230531-04-p0.en+FX+999", "domain": ".google.com", "path": "/"},
            {"name": "SOCS", "value": "CAISHAgBEhJnd3NfMjAyMzA4MTAtMF9SQzIaAmVuIAEaBgiA_LmmBg", "domain": ".google.com", "path": "/"}
        ])
        
        page = context.new_page()
        
        print("正在打开 Google Scholar 页面...")
        page.goto(URL, wait_until="domcontentloaded", timeout=40000)
        
        print("当前页面标题:", page.title())
        print("当前页面URL:", page.url)
        
        # 等待页面渲染出数据
        page.wait_for_timeout(3000)
        html = page.content()
        browser.close()

    # 提取数字
    pattern = r'<td class="gsc_rsb_std">(\d+)</td>'
    matches = re.findall(pattern, html)
    print("匹配到的统计结果:", matches)

    if len(matches) >= 3:
        citations = int(matches[0])
        citations_recent = int(matches[1]) if len(matches) >= 6 else 0
        h_index = int(matches[2]) if len(matches) >= 6 else int(matches[1])
        h_index_recent = int(matches[3]) if len(matches) >= 6 else 0
        i10_index = int(matches[4]) if len(matches) >= 6 else int(matches[2])
        i10_index_recent = int(matches[5]) if len(matches) >= 6 else 0

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
    else:
        # 如果未匹配到，打印出前 500 个字符方便看原因
        print("HTML内容片段:", html[:500])
        raise RuntimeError(f"未能匹配到统计数据，页面标题: {page.title() if 'page' in locals() else '未知'}")

    with open("scholar.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("写入成功！新数据：", data)

if __name__ == "__main__":
    fetch_stats()
