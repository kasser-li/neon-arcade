#!/bin/bash
# 金价查询任务执行脚本
# 由OpenClaw Cron调用

cd /root/.openclaw/workspace/skills/gold-price
python3 task.py
