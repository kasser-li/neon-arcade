#!/usr/bin/env python3
"""
使用 Hugging Face Inference API 生成孙悟空图像
"""

import requests
import os
from datetime import datetime

# 创建输出目录
output_dir = "/root/.openclaw/workspace/img"
os.makedirs(output_dir, exist_ok=True)

# 生成时间戳
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_path = f"{output_dir}/wukong_{timestamp}.png"

# 提示词
prompt = "Sun Wukong, the Monkey King, golden armor, phoenix feather crown, Ruyi Jingu Bang staff, standing on clouds, Chinese mythology, epic, highly detailed"

print(f"正在生成孙悟空图像...")
print(f"提示词: {prompt}")

# 使用 Hugging Face 免费推理 API
API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"

headers = {
    "Authorization": "Bearer hf_demo",
    "Content-Type": "application/json"
}

payload = {
    "inputs": prompt,
    "parameters": {
        "num_inference_steps": 50,
        "guidance_scale": 7.5
    }
}

try:
    response = requests.post(API_URL, headers=headers, json=payload, timeout=120)
    
    if response.status_code == 200:
        # 保存图像
        with open(output_path, "wb") as f:
            f.write(response.content)
        
        file_size = os.path.getsize(output_path)
        print(f"✅ 图像生成成功!")
        print(f"文件大小: {file_size / 1024:.1f} KB")
        print(f"保存位置: {output_path}")
    else:
        print(f"❌ API 错误: {response.status_code}")
        print(response.text)
        exit(1)
        
except Exception as e:
    print(f"❌ 生成失败: {e}")
    exit(1)
