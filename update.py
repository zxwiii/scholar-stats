import json
import re
import time
from datetime import datetime, timezone, timedelta
from playwright.sync_api import sync_playwright

SCHOLAR_ID = "RzJmjLkAAAAJ"
URL = f"https://scholar.google.com/citations?user={SCHOLAR_ID}&hl=en"

def fetch_stats():
    last_error = None
    data = None
    
    # 增加最多 3 次重试机制
    for attempt in range(1, 4):
        print(f"开始第 {attempt} 次尝试获取 Google Scholar 数据...")
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(
                    headless=True,
                    args=["--disable-blink-features=AutomationControlled", "--no-sandbox"]
                )
                context = browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                    locale="en-US"
                )
                page = context.new_page()
                
                # 改用 domcontentloaded，DOM加载完毕即读取，绝不卡 networkidle 超时
                page.goto(URL, wait_until="domcontentloaded", timeout=30000)
                
                # 兼容处理海外 Google 的隐私/Cookie 弹窗
                try:
                    accept_btn = page.locator('button:has-text("Accept all"), button:has-text("I agree")').first
                    if accept_btn.is_visible(timeout=2000):
                        accept_btn.click()
                        time.sleep(1)
                except Exception:
                    pass
                
                page.wait_for_selector("#gsc_rsb_st", timeout=15000)
                html = page.content()
                browser.close()

            # 解析数据
            pattern = r'<td class="gsc_rsb_std">(\d+)</td>'
            matches = re.findall(pattern, html)

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
                print("抓取成功！数据：", data)
                break
        except Exception as e:
            print(f"第 {attempt} 次抓取遇到异常: {e}")
            last_error = e
            time.sleep(3)

    if not data:
        raise RuntimeError(f"连续 3 次尝试均失败，原因: {last_error}")

    # 写入文件
    with open("scholar.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    fetch_stats()
