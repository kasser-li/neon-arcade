#!/usr/bin/env python3
"""
金价查询定时任务
每天10点执行，获取金价并推送到飞书群
使用 agent-browser 从 eyfox.com 获取实时金价
"""

import subprocess
import json
from datetime import datetime

def fetch_gold_price():
    """使用 agent-browser 从 eyfox.com 获取金价数据"""
    try:
        # 打开网页
        result = subprocess.run(
            ["agent-browser", "open", "https://www.eyfox.com/"],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode != 0:
            print(f"打开网页失败: {result.stderr}", flush=True)
            return None
        
        # 等待页面加载
        subprocess.run(
            ["agent-browser", "wait", "--load", "networkidle"],
            capture_output=True, timeout=30
        )
        
        # 获取页面文本内容
        result = subprocess.run(
            ["agent-browser", "eval", "document.body.innerText"],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode != 0:
            print(f"获取页面内容失败: {result.stderr}", flush=True)
            return None
        
        # 关闭浏览器
        subprocess.run(
            ["agent-browser", "close"],
            capture_output=True, timeout=10
        )
        
        # 解析文本内容提取金价
        # 输出被包裹在双引号中，需要处理
        content = result.stdout.strip()
        if content.startswith('"') and content.endswith('"'):
            content = content[1:-1]
        # 将 \n 转换为实际换行
        content = content.replace('\\n', '\n')
        
        # 提取数据
        data = {
            'rate': None,
            'gold_usd': None,
            'silver_usd': None,
            'update_time': None
        }
        
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if '美元/人民币' in line and i + 1 < len(lines):
                try:
                    data['rate'] = float(lines[i + 1].strip())
                except:
                    pass
            elif '伦敦金现 (USD/oz)' in line and i + 1 < len(lines):
                try:
                    data['gold_usd'] = float(lines[i + 1].strip())
                except:
                    pass
            elif '伦敦银现 (USD/oz)' in line and i + 1 < len(lines):
                try:
                    data['silver_usd'] = float(lines[i + 1].strip())
                except:
                    pass
            elif '更新时间' in line and i + 1 < len(lines):
                data['update_time'] = lines[i + 1].strip()
        
        # 计算人民币克价 (1 oz = 31.1034768 g)
        if data['gold_usd'] and data['rate']:
            data['gold_cny_per_gram'] = round(data['gold_usd'] * data['rate'] / 31.1034768, 2)
        
        if data['silver_usd'] and data['rate']:
            data['silver_cny_per_gram'] = round(data['silver_usd'] * data['rate'] / 31.1034768, 2)
        
        return data if data['gold_usd'] else None
        
    except Exception as e:
        print(f"获取金价数据失败: {e}", flush=True)
        import traceback
        traceback.print_exc()
        return None

def format_message(data):
    """格式化金价报告"""
    lines = []
    
    lines.append("📊 **今日金价报告**")
    lines.append("")
    
    # 国际金价
    lines.append("🌍 **国际金价（伦敦金/银）**")
    lines.append("")
    lines.append(f"| 品种 | 美元/盎司 | 人民币/克 |")
    lines.append(f"|------|----------|----------|")
    lines.append(f"| 黄金 | {data['gold_usd']} | {data.get('gold_cny_per_gram', '-')} |")
    lines.append(f"| 白银 | {data['silver_usd']} | {data.get('silver_cny_per_gram', '-')} |")
    lines.append("")
    
    # 汇率信息
    lines.append("💱 **汇率信息**")
    lines.append("")
    lines.append(f"- 美元/人民币汇率: {data['rate']}")
    lines.append(f"- 换算公式: 1 盎司 = 31.1034768 克")
    lines.append("")
    
    lines.append("---")
    update_time = data.get('update_time', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    lines.append(f"🐾 数据来源: eyfox.com | 更新时间: {update_time}")
    
    return "\n".join(lines)

def main():
    """主函数"""
    data = fetch_gold_price()
    if data:
        message = format_message(data)
        print(message)
        return 0
    else:
        print("❌ 获取金价数据失败，请检查 agent-browser 是否正常工作")
        return 1

if __name__ == "__main__":
    exit(main())
