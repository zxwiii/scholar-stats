import json
import re
import os
import time
from datetime import datetime, timezone, timedelta
from playwright.sync_api import sync_playwright

SCHOLAR_ID = "RzJmjLkAAAAJ"
URL = f"https://scholar.google.com/citations?user={SCHOLAR_ID}&hl=en"

def fetch_stats():
    data = None
    with sync_playwright() as p:
        # 启动真实浏览器
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox"
            ]
        )
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            locale="en-US",
            viewport={"width": 1280, "height": 800}
        )
        page = context.new_page()
        
        try:
            print("正在访问 Google Scholar 页面...")
            page.goto(URL, wait_until="networkidle", timeout=45000)
            
            # 如果有 Google 隐私政策/Cookie 同意按钮，自动点击接受
            for selector in ['button:has-text("Accept all")', 'button:has-text("I agree")', 'button[aria-label="Accept all"]']:
                if page.locator(selector).is_visible():
                    try:
                        page.locator(selector).click(timeout=3000)
                        time.sleep(1)
                    except Exception:
                        pass
            
            # 等待统计表格出现
            page.wait_for_selector("#gsc_rsb_st", timeout=25000)
            html = page.content()
            
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
                matches = []
                
            if matches:
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
        except Exception as e:
            print("本轮访问遇到延迟或风控拦截:", e)
        finally:
            browser.close()

    # 结果写入与容错保底机制
    if data:
        with open("scholar.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("抓取成功！数据内容已写入：", data)
    else:
        # 如果偶发被风控，保留现有旧数据文件，保证 Action 保持绿色正常
        if os.path.exists("scholar.json"):
            print("偶发网络波动或反爬，已安全保留上一版正常数据，将在下次定时计划中重试。")
        else:
            raise RuntimeError("首次抓取未成功，且本地无旧数据文件。")

if __name__ == "__main__":
    fetch_stats()
