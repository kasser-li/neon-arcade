#!/usr/bin/env python3
"""
小红书登录管理器
- 生成登录二维码
- 等待用户扫码
- 自动获取 cookies
"""

import asyncio
import json
import os
import time
from pathlib import Path

# 使用 Playwright
from playwright.async_api import async_playwright

class XHSLoginManager:
    def __init__(self, user_id):
        self.user_id = user_id
        self.qr_path = f"/tmp/xhs_qr_{user_id}_{int(time.time())}.png"
        self.cookies_path = f"/root/.openclaw/workspace/xiaohongshu_users/{user_id}"
        
    async def generate_login_qr(self):
        """生成登录二维码"""
        async with async_playwright() as p:
            # 启动浏览器
            browser = await p.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-dev-shm-usage']
            )
            context = await browser.new_context(viewport={'width': 1280, 'height': 720})
            page = await context.new_page()
            
            # 访问小红书
            await page.goto('https://www.xiaohongshu.com/explore', wait_until='networkidle')
            
            # 等待二维码出现
            await page.wait_for_selector('.qrcode-img, img[class*="qr"], canvas[class*="qr"]', timeout=30000)
            
            # 获取二维码元素
            qr_element = await page.query_selector('.qrcode-img, img[class*="qr"], canvas[class*="qr"]')
            
            if qr_element:
                # 截图保存二维码
                await qr_element.screenshot(path=self.qr_path)
                print(f"QR_CODE_PATH:{self.qr_path}")
                
                # 等待用户扫码（最多120秒）
                print("WAITING_FOR_LOGIN:120")
                await asyncio.sleep(120)
                
                # 检查是否登录成功
                cookies = await context.cookies()
                xhs_cookies = {c['name']: c['value'] for c in cookies if 'xiaohongshu' in c.get('domain', '')}
                
                if 'a1' in xhs_cookies:
                    # 保存 cookies
                    Path(self.cookies_path).mkdir(parents=True, exist_ok=True)
                    with open(f"{self.cookies_path}/cookies.json", 'w') as f:
                        json.dump(xhs_cookies, f)
                    print(f"LOGIN_SUCCESS:{self.user_id}")
                    return True
                else:
                    print("LOGIN_TIMEOUT")
                    return False
            else:
                print("QR_CODE_NOT_FOUND")
                return False
            
            await browser.close()

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python xhs_login_manager.py <user_id>")
        sys.exit(1)
    
    user_id = sys.argv[1]
    manager = XHSLoginManager(user_id)
    asyncio.run(manager.generate_login_qr())
