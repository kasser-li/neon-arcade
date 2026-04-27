#!/usr/bin/env python3
"""
小红书登录助手 (飞书账号绑定版)
自动截取登录二维码、保存登录态(cookie)并绑定到飞书用户
"""

from playwright.sync_api import sync_playwright
from datetime import datetime, timedelta
import time
import os
import sys
import json

# 配置
FEISHU_DOC_TOKEN = "MilPdHYtvoCG7sxZOldcLUdQnuf"
QR_CODE_DIR = "/tmp/xhs_qrcodes"
COOKIE_BASE_DIR = "/root/.openclaw/workspace/cookies"
QR_VALID_MINUTES = 5
COOKIE_VALID_DAYS = 7


def ensure_dir(directory):
    """确保目录存在"""
    if not os.path.exists(directory):
        os.makedirs(directory)


def get_user_cookie_dir(feishu_user_id):
    """获取指定飞书用户的cookie目录"""
    user_dir = os.path.join(COOKIE_BASE_DIR, feishu_user_id)
    ensure_dir(user_dir)
    return user_dir


def cleanup_old_qrcodes(directory, keep_last=3):
    """清理旧的二维码文件"""
    try:
        files = []
        for f in os.listdir(directory):
            if f.startswith("xhs_qr_") and f.endswith(".png"):
                filepath = os.path.join(directory, f)
                files.append((filepath, os.path.getmtime(filepath)))
        files.sort(key=lambda x: x[1], reverse=True)
        for filepath, _ in files[keep_last:]:
            try:
                os.remove(filepath)
                print(f"已清理旧二维码: {filepath}")
            except:
                pass
    except:
        pass


def load_cookies(feishu_user_id):
    """加载指定飞书用户的cookie"""
    user_dir = get_user_cookie_dir(feishu_user_id)
    cookie_file = os.path.join(user_dir, "xiaohongshu_cookies.json")
    
    if not os.path.exists(cookie_file):
        return None
    
    try:
        with open(cookie_file, 'r') as f:
            data = json.load(f)
        
        saved_time = datetime.fromisoformat(data.get('saved_at', '2000-01-01'))
        expires_time = saved_time + timedelta(days=COOKIE_VALID_DAYS)
        
        if datetime.now() > expires_time:
            print(f"Cookie已过期（保存时间: {saved_time}）")
            return None
        
        print(f"✅ 找到有效Cookie（保存时间: {saved_time}，有效期至: {expires_time}）")
        return data.get('cookies', [])
    
    except Exception as e:
        print(f"加载cookie失败: {e}")
        return None


def save_cookies(cookies, feishu_user_id):
    """保存cookie到指定飞书用户的目录"""
    user_dir = get_user_cookie_dir(feishu_user_id)
    cookie_file = os.path.join(user_dir, "xiaohongshu_cookies.json")
    
    try:
        data = {
            'saved_at': datetime.now().isoformat(),
            'expires_days': COOKIE_VALID_DAYS,
            'feishu_user_id': feishu_user_id,
            'cookies': cookies
        }
        
        with open(cookie_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"✅ Cookie已保存: {cookie_file}")
        print(f"⏰ 有效期: {COOKIE_VALID_DAYS}天")
    except Exception as e:
        print(f"❌ 保存cookie失败: {e}")


def check_login_status(page):
    """检查小红书登录状态"""
    try:
        selectors = ['img[class*="avatar"]', '[class*="user-info"]', 'text=退出登录']
        for selector in selectors:
            try:
                if page.locator(selector).first.is_visible():
                    return True
            except:
                pass
        if '/login' not in page.url and '/explore' in page.url:
            return True
        return False
    except:
        return False


def capture_xhs_qrcode_and_wait(feishu_user_id):
    """截取小红书登录二维码并等待登录完成"""
    ensure_dir(QR_CODE_DIR)
    cleanup_old_qrcodes(QR_CODE_DIR)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    qr_filename = f"xhs_qr_{timestamp}.png"
    qr_path = os.path.join(QR_CODE_DIR, qr_filename)
    
    cookies = None
    login_success = False
    used_existing_cookie = False
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={'width': 1280, 'height': 900},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        )
        page = context.new_page()
        
        # 尝试加载该飞书用户的cookie
        existing_cookies = load_cookies(feishu_user_id)
        if existing_cookies:
            print(f"尝试使用用户 {feishu_user_id} 的Cookie登录...")
            context.add_cookies(existing_cookies)
            page.goto('https://www.xiaohongshu.com')
            time.sleep(3)
            if check_login_status(page):
                print("✅ Cookie有效，已自动登录！")
                login_success = True
                used_existing_cookie = True
                cookies = existing_cookies
            else:
                print("Cookie已失效，需要重新扫码")
        
        # 需要重新登录
        if not login_success:
            print("正在打开小红书登录页...")
            page.goto('https://www.xiaohongshu.com')
            time.sleep(2)
            
            try:
                login_btn = page.locator('text=登录').first
                if login_btn.is_visible():
                    login_btn.click()
                    time.sleep(4)
            except:
                pass
            
            login_popup = page.locator('div[class*="login"]').first
            all_elements = login_popup.locator('*').all()
            qr_element = None
            
            for elem in all_elements:
                try:
                    elem_box = elem.bounding_box()
                    if elem_box:
                        w, h = elem_box['width'], elem_box['height']
                        if 150 <= w <= 250 and 150 <= h <= 250 and abs(w - h) <= 10:
                            elem.screenshot(path=qr_path)
                            qr_element = elem
                            print(f"✅ 已保存二维码: {w}x{h}")
                            break
                except:
                    pass
            
            if not qr_element:
                browser.close()
                return None
            
            print("\n⏳ 等待扫码登录（最多60秒）...")
            
            for i in range(60):
                time.sleep(1)
                if check_login_status(page):
                    print(f"\n✅ 登录成功！（用时{i+1}秒）")
                    login_success = True
                    break
            
            if login_success:
                cookies = context.cookies()
                save_cookies(cookies, feishu_user_id)
        
        browser.close()
        
        return {
            'path': qr_path if not used_existing_cookie else None,
            'generated_at': datetime.now(),
            'expires_at': datetime.now() + timedelta(minutes=QR_VALID_MINUTES),
            'cookies': cookies,
            'login_success': login_success,
            'used_existing_cookie': used_existing_cookie,
            'feishu_user_id': feishu_user_id
        }


def main():
    # 从环境变量或参数获取飞书用户ID
    feishu_user_id = os.environ.get('FEISHU_USER_ID') or sys.argv[1] if len(sys.argv) > 1 else None
    
    if not feishu_user_id:
        print("❌ 请提供飞书用户ID")
        print("用法: python xhs_login_helper.py <feishu_user_id>")
        print("或设置环境变量: FEISHU_USER_ID=ou_xxx python xhs_login_helper.py")
        sys.exit(1)
    
    print("🚀 小红书登录助手启动...")
    print(f"👤 飞书用户: {feishu_user_id}")
    print(f"📁 Cookie目录: {get_user_cookie_dir(feishu_user_id)}")
    print("-" * 50)
    
    result = capture_xhs_qrcode_and_wait(feishu_user_id)
    
    if not result:
        print("❌ 登录失败")
        sys.exit(1)
    
    if result['used_existing_cookie']:
        print(f"\n✅ 用户 {feishu_user_id} 使用Cookie自动登录成功！")
    else:
        print(f"\n✅ 用户 {feishu_user_id} 扫码登录成功！")
        print(f"📁 二维码: {result['path']}")
    
    print(f"\n💡 下次运行将自动使用该用户的Cookie登录（{COOKIE_VALID_DAYS}天内有效）")
    return result


if __name__ == '__main__':
    main()
