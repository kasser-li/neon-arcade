# Gold Price Reporter Skill

每天10点自动查询金价并推送到飞书群

## 功能
- 使用 agent-browser 从 eyfox.com 获取实时金价数据
- 获取伦敦金/银价格（美元/盎司）
- 自动换算为人民币/克价格
- 推送到指定的飞书群

## 配置
- 定时：每天 10:00
- 目标群：oc_563dcb743a08d6bacf456a3457bf84b6
- 数据源：eyfox.com（伦敦金/银现货价格）

## 更新记录
- 2026-03-30: 更换数据源，从 xxapi.cn 改为 eyfox.com（使用 agent-browser 获取）
