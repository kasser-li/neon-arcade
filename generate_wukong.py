#!/usr/bin/env python3
"""
使用 pollinations.ai 免费 API 生成孙悟空图像
"""

import urllib.request
import urllib.parse
import os
from datetime import datetime

# 创建输出目录
output_dir = "/root/.openclaw/workspace/img"
os.makedirs(output_dir, exist_ok=True)

# 生成时间戳
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_path = f"{output_dir}/wukong_{timestamp}.png"

# 构建提示词
prompt = "Sun Wukong, the Monkey King, wearing golden armor and phoenix-feather cap, holding the Ruyi Jingu Bang staff, standing on clouds, powerful and majestic, Chinese mythology style, highly detailed, 4K quality, epic composition"

# URL 编码提示词
encoded_prompt = urllib.parse.quote(prompt)

# Pollinations.ai 免费图像生成 API
url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&seed=42&nologo=true"

print(f"正在生成孙悟空图像...")
print(f"提示词: {prompt}")
print(f"保存路径: {output_path}")

try:
    # 下载图像
    req = urllib.request.Request(
        url,
        headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.0'
        }
    )
    
    with urllib.request.urlopen(req, timeout=120) as response:
        with open(output_path, 'wb') as f:
            f.write(response.read())
    
    # 检查文件大小
    file_size = os.path.getsize(output_path)
    print(f"✅ 图像生成成功!")
    print(f"文件大小: {file_size / 1024:.1f} KB")
    print(f"保存位置: {output_path}")
    
except Exception as e:
    print(f"❌ 生成失败: {e}")
    exit(1)
