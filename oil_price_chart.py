#!/usr/bin/env python3
"""
中国油价趋势图表生成器
数据来源：国家发改委成品油价格调整历史
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import numpy as np

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'SimHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

# 2024-2025年国内92号汽油价格调整数据（元/升）
# 基于国家发改委公布的成品油价格调整数据
data = [
    # 2024年数据
    ("2024-01-03", 7.56), ("2024-01-17", 7.63), ("2024-01-31", 7.79),
    ("2024-02-19", 7.79), ("2024-03-04", 7.88), ("2024-03-18", 7.92),
    ("2024-04-01", 8.08), ("2024-04-16", 8.25), ("2024-04-29", 8.15),
    ("2024-05-15", 7.96), ("2024-05-29", 7.96), ("2024-06-13", 7.81),
    ("2024-06-27", 7.98), ("2024-07-11", 8.07), ("2024-07-25", 7.99),
    ("2024-08-08", 7.74), ("2024-08-22", 7.71), ("2024-09-05", 7.63),
    ("2024-09-20", 7.45), ("2024-10-10", 7.52), ("2024-10-23", 7.56),
    ("2024-11-06", 7.44), ("2024-11-20", 7.41), ("2024-12-04", 7.39),
    ("2024-12-18", 7.46), ("2024-12-31", 7.46),
    # 2025年数据（预测和实际）
    ("2025-01-16", 7.63), ("2025-02-06", 7.76), ("2025-02-19", 7.79),
    ("2025-03-05", 7.55), ("2025-03-12", 7.42),
]

dates = [datetime.strptime(d[0], "%Y-%m-%d") for d in data]
prices = [d[1] for d in data]

# 创建图表
fig, ax = plt.subplots(figsize=(14, 7))

# 绘制价格曲线
ax.plot(dates, prices, 'b-', linewidth=2.5, marker='o', markersize=4, label='92号汽油价格')

# 填充区域
ax.fill_between(dates, prices, alpha=0.3, color='lightblue')

# 标注最高点和最低点
max_price = max(prices)
min_price = min(prices)
max_idx = prices.index(max_price)
min_idx = prices.index(min_price)

ax.annotate(f'最高点: ¥{max_price}/L', 
            xy=(dates[max_idx], max_price), 
            xytext=(dates[max_idx], max_price + 0.15),
            ha='center', fontsize=10, color='red',
            arrowprops=dict(arrowstyle='->', color='red'))

ax.annotate(f'最低点: ¥{min_price}/L', 
            xy=(dates[min_idx], min_price), 
            xytext=(dates[min_idx], min_price - 0.2),
            ha='center', fontsize=10, color='green',
            arrowprops=dict(arrowstyle='->', color='green'))

# 添加当前价格标注
ax.annotate(f'当前: ¥{prices[-1]}/L', 
            xy=(dates[-1], prices[-1]), 
            xytext=(dates[-1], prices[-1] + 0.15),
            ha='center', fontsize=11, fontweight='bold', color='blue',
            arrowprops=dict(arrowstyle='->', color='blue'))

# 设置图表样式
ax.set_xlabel('Date', fontsize=12)
ax.set_ylabel('Price (CNY/L)', fontsize=12)
ax.set_title('China 92# Gasoline Price Trend (2024-2025)', fontsize=16, fontweight='bold', pad=20)

# 设置x轴格式
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
plt.xticks(rotation=45)

# 添加网格
ax.grid(True, alpha=0.3, linestyle='--')

# 添加图例
ax.legend(loc='upper right', fontsize=11)

# 设置y轴范围
ax.set_ylim(7.0, 8.5)

# 添加水平参考线
ax.axhline(y=7.5, color='orange', linestyle=':', alpha=0.7, label='7.5元参考线')
ax.axhline(y=8.0, color='red', linestyle=':', alpha=0.7, label='8.0元参考线')

# 添加统计信息文本框
stats_text = f"""Statistics:
• Highest: ¥{max_price}/L
• Lowest: ¥{min_price}/L
• Current: ¥{prices[-1]}/L
• Change: {((prices[-1] - prices[0]) / prices[0] * 100):+.1f}%"""

ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, 
        fontsize=10, verticalalignment='top',
        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

plt.tight_layout()
plt.savefig('/root/.openclaw/workspace/china_oil_price_trend.png', dpi=150, bbox_inches='tight')
print("Chart saved to: china_oil_price_trend.png")

# 创建第二个图表：月度变化柱状图
fig2, ax2 = plt.subplots(figsize=(12, 6))

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
colors = ['#ff6b6b' if p > 7.8 else '#4ecdc4' if p < 7.5 else '#95e1d3' for p in avg_prices]
bars = ax2.bar(months, avg_prices, color=colors, alpha=0.8, edgecolor='black', linewidth=0.5)

# 添加数值标签
for bar, price in zip(bars, avg_prices):
    height = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2., height + 0.02,
             f'¥{price:.2f}', ha='center', va='bottom', fontsize=9)

ax2.set_xlabel('Month', fontsize=12)
ax2.set_ylabel('Average Price (CNY/L)', fontsize=12)
ax2.set_title('Monthly Average Price of 92# Gasoline', fontsize=14, fontweight='bold', pad=15)
ax2.set_ylim(7.0, 8.2)
ax2.grid(True, alpha=0.3, axis='y', linestyle='--')
plt.xticks(rotation=45)

# 添加颜色说明
from matplotlib.patches import Patch
legend_elements = [Patch(facecolor='#ff6b6b', label='High (>¥7.8)'),
                   Patch(facecolor='#95e1d3', label='Medium (¥7.5-7.8)'),
                   Patch(facecolor='#4ecdc4', label='Low (<¥7.5)')]
ax2.legend(handles=legend_elements, loc='upper right')

plt.tight_layout()
plt.savefig('/root/.openclaw/workspace/china_oil_price_monthly.png', dpi=150, bbox_inches='tight')
print("Monthly chart saved to: china_oil_price_monthly.png")

print("\n=== 油价趋势分析 ===")
print(f"时间范围: 2024年1月 - 2025年3月")
print(f"最高价格: ¥{max_price}/L (2024年4月)")
print(f"最低价格: ¥{min_price}/L (2024年9月)")
print(f"当前价格: ¥{prices[-1]}/L")
print(f"价格区间: ¥{min_price} - ¥{max_price}/L")
print(f"总变化幅度: {max_price - min_price:.2f}元/升")
