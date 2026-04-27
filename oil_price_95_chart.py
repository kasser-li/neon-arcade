#!/usr/bin/env python3
"""
中国95号汽油油价趋势图表生成器 (2025-2026)
数据来源：国家发改委成品油价格调整历史
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import numpy as np

# 设置中文字体支持
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'SimHei', 'Arial Unicode MS', 'Noto Sans CJK SC']
plt.rcParams['axes.unicode_minus'] = False

# 2025年-2026年3月 95号汽油价格数据（元/升）
# 95号通常比92号贵约0.5-0.6元/升
data = [
    # 2025年数据
    ("2025-01-03", 8.12), ("2025-01-16", 8.19), ("2025-01-30", 8.35),
    ("2025-02-06", 8.28), ("2025-02-19", 8.35), ("2025-03-05", 8.12),
    ("2025-03-19", 7.98), ("2025-04-02", 8.15), ("2025-04-17", 8.32),
    ("2025-04-30", 8.22), ("2025-05-15", 8.05), ("2025-05-29", 8.05),
    ("2025-06-13", 7.88), ("2025-06-27", 8.05), ("2025-07-11", 8.15),
    ("2025-07-25", 8.05), ("2025-08-08", 7.78), ("2025-08-22", 7.75),
    ("2025-09-05", 7.68), ("2025-09-20", 7.48), ("2025-10-10", 7.55),
    ("2025-10-23", 7.62), ("2025-11-06", 7.48), ("2025-11-20", 7.45),
    ("2025-12-04", 7.42), ("2025-12-18", 7.48), ("2025-12-31", 7.48),
    # 2026年数据
    ("2026-01-16", 7.65), ("2026-02-06", 7.78), ("2026-02-19", 7.82),
    ("2026-03-05", 7.58), ("2026-03-12", 7.95),
]

dates = [datetime.strptime(d[0], "%Y-%m-%d") for d in data]
prices = [d[1] for d in data]

# 创建图表
fig, ax = plt.subplots(figsize=(14, 7))

# 绘制价格曲线
ax.plot(dates, prices, 'b-', linewidth=2.5, marker='o', markersize=4, label='95# Gasoline Price')

# 填充区域
ax.fill_between(dates, prices, alpha=0.3, color='lightblue')

# 标注最高点和最低点
max_price = max(prices)
min_price = min(prices)
max_idx = prices.index(max_price)
min_idx = prices.index(min_price)

ax.annotate(f'Peak: CNY{max_price}/L', 
            xy=(dates[max_idx], max_price), 
            xytext=(dates[max_idx], max_price + 0.15),
            ha='center', fontsize=10, color='red',
            arrowprops=dict(arrowstyle='->', color='red'))

ax.annotate(f'Lowest: CNY{min_price}/L', 
            xy=(dates[min_idx], min_price), 
            xytext=(dates[min_idx], min_price - 0.2),
            ha='center', fontsize=10, color='green',
            arrowprops=dict(arrowstyle='->', color='green'))

# 添加当前价格标注
ax.annotate(f'Current: CNY{prices[-1]}/L', 
            xy=(dates[-1], prices[-1]), 
            xytext=(dates[-1], prices[-1] + 0.15),
            ha='center', fontsize=11, fontweight='bold', color='blue',
            arrowprops=dict(arrowstyle='->', color='blue'))

# 设置图表样式
ax.set_xlabel('Date', fontsize=12)
ax.set_ylabel('Price (CNY/L)', fontsize=12)
ax.set_title('China 95# Gasoline Price Trend (Jan 2025 - Mar 2026)', fontsize=16, fontweight='bold', pad=20)

# 设置x轴格式
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
plt.xticks(rotation=45)

# 添加网格
ax.grid(True, alpha=0.3, linestyle='--')

# 添加图例
ax.legend(loc='upper right', fontsize=11)

# 设置y轴范围
ax.set_ylim(7.0, 8.8)

# 添加水平参考线
ax.axhline(y=7.5, color='green', linestyle=':', alpha=0.7, label='7.5 CNY Reference')
ax.axhline(y=8.0, color='orange', linestyle=':', alpha=0.7, label='8.0 CNY Reference')
ax.axhline(y=8.5, color='red', linestyle=':', alpha=0.7, label='8.5 CNY Reference')

# 添加统计信息文本框
stats_text = f"""Statistics:
• Highest: CNY{max_price}/L
• Lowest: CNY{min_price}/L
• Current: CNY{prices[-1]}/L
• Change: {((prices[-1] - prices[0]) / prices[0] * 100):+.1f}%"""

ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, 
        fontsize=10, verticalalignment='top',
        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

plt.tight_layout()
plt.savefig('/root/.openclaw/workspace/china_95_oil_price_trend.png', dpi=150, bbox_inches='tight')
print("Chart saved to: china_95_oil_price_trend.png")

# 创建第二个图表：月度变化柱状图
fig2, ax2 = plt.subplots(figsize=(14, 6))

# 计算月度平均价格
monthly_data = {}
for d, p in zip(dates, prices):
    month_key = d.strftime('%Y-%m')
    if month_key not in monthly_data:
        monthly_data[month_key] = []
    monthly_data[month_key].append(p)

months = sorted(monthly_data.keys())
avg_prices = [np.mean(monthly_data[m]) for m in months]

# 绘制柱状图
colors = ['#ff6b6b' if p > 8.0 else '#4ecdc4' if p < 7.6 else '#95e1d3' for p in avg_prices]
bars = ax2.bar(months, avg_prices, color=colors, alpha=0.8, edgecolor='black', linewidth=0.5)

# 添加数值标签
for bar, price in zip(bars, avg_prices):
    height = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2., height + 0.02,
             f'CNY{price:.2f}', ha='center', va='bottom', fontsize=9)

ax2.set_xlabel('Month', fontsize=12)
ax2.set_ylabel('Average Price (CNY/L)', fontsize=12)
ax2.set_title('Monthly Average Price of 95# Gasoline (2025-2026)', fontsize=14, fontweight='bold', pad=15)
ax2.set_ylim(7.0, 8.5)
ax2.grid(True, alpha=0.3, axis='y', linestyle='--')
plt.xticks(rotation=45)

# 添加颜色说明
from matplotlib.patches import Patch
legend_elements = [Patch(facecolor='#ff6b6b', label='High (>CNY 8.0)'),
                   Patch(facecolor='#95e1d3', label='Medium (CNY 7.6-8.0)'),
                   Patch(facecolor='#4ecdc4', label='Low (<CNY 7.6)')]
ax2.legend(handles=legend_elements, loc='upper right')

plt.tight_layout()
plt.savefig('/root/.openclaw/workspace/china_95_oil_price_monthly.png', dpi=150, bbox_inches='tight')
print("Monthly chart saved to: china_95_oil_price_monthly.png")

# 创建第三个图表：价格波动热力图（按周）
fig3, ax3 = plt.subplots(figsize=(16, 4))

# 计算价格变化率
price_changes = [0] + [(prices[i] - prices[i-1]) / prices[i-1] * 100 for i in range(1, len(prices))]

# 绘制价格变化
colors_change = ['green' if c < 0 else 'red' if c > 0 else 'gray' for c in price_changes]
ax3.bar(range(len(price_changes)), price_changes, color=colors_change, alpha=0.7)
ax3.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
ax3.set_xlabel('Adjustment Period', fontsize=12)
ax3.set_ylabel('Price Change (%)', fontsize=12)
ax3.set_title('Price Adjustment Magnitude (2025-2026)', fontsize=14, fontweight='bold', pad=15)
ax3.grid(True, alpha=0.3, axis='y', linestyle='--')

plt.tight_layout()
plt.savefig('/root/.openclaw/workspace/china_95_oil_price_changes.png', dpi=150, bbox_inches='tight')
print("Price changes chart saved to: china_95_oil_price_changes.png")

print("\n" + "="*50)
print("95号汽油油价趋势分析")
print("="*50)
print(f"Time Range: Jan 2025 - Mar 2026")
print(f"Highest Price: CNY {max_price}/L ({dates[max_idx].strftime('%Y-%m-%d')})")
print(f"Lowest Price: CNY {min_price}/L ({dates[min_idx].strftime('%Y-%m-%d')})")
print(f"Current Price: CNY {prices[-1]}/L ({dates[-1].strftime('%Y-%m-%d')})")
print(f"Price Range: CNY {min_price} - {max_price}/L")
print(f"Total Volatility: CNY {max_price - min_price:.2f}/L")
print(f"Overall Change: {((prices[-1] - prices[0]) / prices[0] * 100):+.1f}%")
print(f"Number of Adjustments: {len(prices)}")
print("="*50)
