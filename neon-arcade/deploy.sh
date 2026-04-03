#!/bin/bash

echo "🚀 Neon Arcade 一键打包部署脚本"
echo "================================"

# 1. 打包
echo "📦 步骤 1/3: 打包项目..."
cd /root/.openclaw/workspace/neon-arcade/apps/web
npm run build
if [ $? -ne 0 ]; then
    echo "❌ 打包失败！"
    exit 1
fi
echo "✅ 打包完成"

# 2. 复制到部署目录
echo "📂 步骤 2/3: 复制到部署目录..."
# 保留 server.py
if [ -f /root/.openclaw/workspace/games/server.py ]; then
    cp /root/.openclaw/workspace/games/server.py /tmp/server.py.bak
fi
rm -rf /root/.openclaw/workspace/games/*
cp -r dist/* /root/.openclaw/workspace/games/
# 关键：复制游戏文件到 games/games/
mkdir -p /root/.openclaw/workspace/games/games
cp -r public/* /root/.openclaw/workspace/games/games/ 2>/dev/null || echo "⚠️ 检查 public 目录"
# 恢复 server.py
if [ -f /tmp/server.py.bak ]; then
    cp /tmp/server.py.bak /root/.openclaw/workspace/games/server.py
    rm /tmp/server.py.bak
fi
echo "✅ 复制完成"

# 3. 重启服务
echo "🔄 步骤 3/3: 重启 HTTP 服务..."
pkill -f "python3.*http.server.*8888" 2>/dev/null
pkill -f "server.py" 2>/dev/null
sleep 1
cd /root/.openclaw/workspace/games
# 使用支持SPA的服务器脚本
nohup python3 /root/.openclaw/workspace/games/server.py > /dev/null 2>&1 &
echo "✅ 服务已重启"

echo ""
echo "🎉 部署完成！"
echo "访问地址: http://49.235.120.204:8888"
