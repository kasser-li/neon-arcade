#!/bin/bash
set -e

echo "🎮 开始搭建 Neon Arcade 项目..."

# 创建目录结构
mkdir -p /root/.openclaw/workspace/neon-arcade/{apps,packages,server}
echo "✅ 目录结构创建完成"

# 进入项目目录
cd /root/.openclaw/workspace/neon-arcade

# 创建根 package.json
cat > package.json << 'EOF'
{
  "name": "neon-arcade",
  "version": "1.0.0",
  "description": "霓虹游戏站 - 在线小游戏平台",
  "type": "module",
  "scripts": {
    "dev": "cd apps/web && npm run dev",
    "build": "cd apps/web && npm run build",
    "preview": "cd apps/web && npm run preview"
  },
  "workspaces": [
    "apps/*",
    "packages/*"
  ]
}
EOF
echo "✅ 根 package.json 创建完成"

# 创建 apps/web 目录
mkdir -p apps/web
cd apps/web

# 初始化 Vue 项目
echo "📦 初始化 Vue 项目..."
echo -e "\n\n\n\n\n" | npm create vue@latest . -- --typescript --router --pinia

echo "✅ Vue 项目初始化完成"
echo ""
echo "🎉 Neon Arcade 项目搭建完成！"
echo ""
echo "下一步："
echo "  cd /root/.openclaw/workspace/neon-arcade/apps/web"
echo "  npm install"
echo "  npm run dev"
