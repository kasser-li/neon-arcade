#!/bin/bash
# 每日金价查询任务 - 推送到飞书群
# 使用 xxapi.cn 接口获取国内金价

# 飞书群配置
FEISHU_CHAT_ID="oc_563dcb743a08d6bacf456a3457bf84b6"

# 获取金价数据并格式化
MESSAGE=$(curl -s "https://v2.xxapi.cn/api/goldprice" | python3 -c "
import json
import sys
from datetime import datetime

data = json.load(sys.stdin)
if data.get('code') == 200:
    result = data['data']
    
    lines = []
    lines.append('## 📊 今日国内金价报告')
    lines.append('')
    
    # 银行金条价格
    lines.append('### 💰 银行投资金条价格（元/克）')
    lines.append('')
    for item in result.get('bank_gold_bar_price', []):
        lines.append(f\"- {item['bank']}: {item['price']} 元/克\")
    lines.append('')
    
    # 品牌金饰价格 - 使用文本格式避免表格
    lines.append('### 🏪 品牌金饰价格（元/克）')
    lines.append('')
    for item in result.get('precious_metal_price', []):
        brand = item.get('brand', '')
        bullion = item.get('bullion_price', '-')
        gold = item.get('gold_price', '-')
        platinum = item.get('platinum_price', '-')
        lines.append(f\"- {brand}: 金条{bullion} / 饰品{gold} / 铂金{platinum}\")
    lines.append('')
    
    # 黄金回收价格
    lines.append('### ♻️ 黄金回收参考（元/克）')
    lines.append('')
    for item in result.get('gold_recycle_price', [])[:4]:
        lines.append(f\"- {item['gold_type']}: {item['recycle_price']} 元/克\")
    lines.append('')
    lines.append('---')
    lines.append(f\"🐾 数据来源: xxapi.cn | 查询时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}\")
    
    print('\n'.join(lines))
else:
    print('获取金价数据失败')
")

# 使用 OpenClaw 的 message 工具发送消息到飞书群
# 注意：这里需要通过 OpenClaw 的 CLI 或 API 发送
# 由于 cron 环境限制，我们将消息写入文件，由 OpenClaw 守护进程处理

# 将消息写入待发送队列
echo "$MESSAGE" > /root/.openclaw/workspace/gold_price_message.txt

# 同时记录到日志
echo "[$(date '+%Y-%m-%d %H:%M:%S')] 金价数据已获取" >> /root/.openclaw/workspace/gold_price.log
