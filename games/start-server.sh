#!/bin/bash
cd /root/.openclaw/workspace/games
python3 -m http.server 8888 &
echo "游戏服务器已启动！"
echo "访问地址: http://$(curl -s ifconfig.me):8888"
