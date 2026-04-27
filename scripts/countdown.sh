#!/bin/bash
# 倒计时脚本 - 计算距离 2026-05-29 的天数并发送到群聊

TARGET_DATE="2026-05-29"
END_DATE="2026-05-30"
TODAY=$(date +%Y-%m-%d)

# 检查是否已到结束日期
if [[ "$TODAY" >= "$END_DATE" ]]; then
    echo "任务已结束，日期已达到或超过 2026-05-30"
    exit 0
fi

# 计算天数差
TARGET_TS=$(date -d "$TARGET_DATE" +%s)
TODAY_TS=$(date +%s)
DAYS_LEFT=$(( (TARGET_TS - TODAY_TS) / 86400 ))

# 输出消息内容
MESSAGE="📅 距离 2026-05-29 还有 ${DAYS_LEFT} 天"

echo "$MESSAGE"
