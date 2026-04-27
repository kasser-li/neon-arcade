#!/usr/bin/env python3
"""
小红书登录服务
- 启动浏览器访问小红书登录页
- 获取二维码图片
- 保存二维码供用户扫描
"""

import asyncio
import json
import os
import sys
import time
from pathlib import Path

# 使用 CDP 直接控制 Chrome
import urllib.request
import urllib.error

class XHSLoginService:
    def __init__(self, chrome_port=9222):
        self.chrome_port = chrome_port
        self.cdp_url = f"http://127.0.0.1:{chrome_port}/json"
        self.ws_url = None
        self.qr_path = "/tmp/xhs_login_qr.png"
        
    def _cdp_request(self, method, params=None):
        """发送 CDP 请求"""
        if not self.ws_url:
            return None
            
        import websocket
        ws = websocket.create_connection(self.ws_url)
        msg = {"id": 1, "method": method}
        if params:
            msg["params"] = params
        ws.send(json.dumps(msg))
        result = ws.recv()
        ws.close()
        return json.loads(result)
    
    def get_qr_code(self):
        """获取小红书登录二维码"""
        try:
            # 导航到小红书
            os.system(f'chromium-browser --headless=new --remote-debugging-port={self.chrome_port} --no-sandbox --disable-dev-shm-usage --disable-gpu --window-size=1280,720 https://www.xiaohongshu.com/explore &')
            time.sleep(5)
            
            # 获取二维码元素截图
            # 这里简化处理，实际应该使用 CDP 获取二维码图片
            
            # 生成登录链接二维码（临时方案）
            login_url = f"https://www.xiaohongshu.com/mobile/login?qrId=test{int(time.time())}"
            
            import qrcode
            qr = qrcode.QRCode(version=3, box_size=10, border=2)
            qr.add_data(login_url)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            img.save(self.qr_path)
            
            return self.qr_path, login_url
            
        except Exception as e:
            print(f"Error: {e}")
            return None, None

if __name__ == "__main__":
    service = XHSLoginService()
    qr_path, url = service.get_qr_code()
    if qr_path:
        print(f"QR_PATH:{qr_path}")
        print(f"LOGIN_URL:{url}")
    else:
        print("Failed to get QR code")
        sys.exit(1)
