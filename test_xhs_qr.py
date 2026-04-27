#!/usr/bin/env python3
import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            executable_path='/snap/bin/chromium',
            headless=True,
            args=['--no-sandbox', '--disable-dev-shm-usage']
        )
        page = await browser.new_page()
        await page.goto('https://www.xiaohongshu.com/explore')
        await page.wait_for_timeout(5000)
        
        # 截图看看页面
        await page.screenshot(path='/tmp/xhs_page.png')
        print("Screenshot saved to /tmp/xhs_page.png")
        
        await browser.close()

asyncio.run(main())
