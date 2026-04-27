#!/usr/bin/env python3
"""
使用 pollinations.ai 生成孙悟空图像 - 增强版带重试
"""

import urllib.request
import urllib.parse
import os
from datetime import datetime
import time

# 创建输出目录
output_dir = "/root/.openclaw/workspace/img"
os.makedirs(output_dir, exist_ok=True)

# 生成时间戳
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_path = f"{output_dir}/wukong_{timestamp}.png"

# 提示词
prompt = "Sun Wukong Monkey King golden armor cloud epic fantasy"

# URL 编码
encoded_prompt = urllib.parse.quote(prompt)

# 使用 Pollinations AI
url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&seed=123&nologo=true"

print(f"正在生成孙悟空图像...")
print(f"URL: {url[:80]}...")

try:
    req = urllib.request.Request(
        url,
        headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8'
        }
    )
    
    with urllib.request.urlopen(req, timeout=60) as response:
        data = response.read()
        with open(output_path, 'wb') as f:
            f.write(data)
    
    file_size = os.path.getsize(output_path)
    if file_size > 1000:  # 至少1KB
        print(f"✅ 图像生成成功!")
        print(f"文件大小: {file_size / 1024:.1f} KB")
        print(f"保存位置: {output_path}")
    else:
        print(f"❌ 文件太小，可能生成失败")
        exit(1)
        
except Exception as e:
    print(f"❌ 生成失败: {e}")
    exit(1)
