#!/usr/bin/env python3
"""生成小红书登录二维码"""

import qrcode
import sys
import time

def generate_qr(url, output_path):
    """生成二维码图片"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(output_path)
    print(f"二维码已保存到: {output_path}")
    return output_path

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python xiaohongshu_login.py <login_url>")
        sys.exit(1)
    
    login_url = sys.argv[1]
    output = f"/tmp/xhs_qr_{int(time.time())}.png"
    generate_qr(login_url, output)
