#!/usr/bin/env python3
import requests
import json

# MCP endpoint
url = "http://localhost:18060/mcp"

# Initialize session
init_payload = {
    "jsonrpc": "2.0",
    "method": "initialize",
    "params": {
        "protocolVersion": "2024-11-05",
        "capabilities": {},
        "clientInfo": {"name": "xhs-publisher", "version": "1.0"}
    },
    "id": 1
}

response = requests.post(url, json=init_payload)
print("Init response:", response.json())

# Send initialized notification
notify_payload = {
    "jsonrpc": "2.0",
    "method": "notifications/initialized"
}
requests.post(url, json=notify_payload)

# Get tools list
tools_payload = {
    "jsonrpc": "2.0",
    "method": "tools/list",
    "id": 2
}
response = requests.post(url, json=tools_payload)
print("Tools list:", response.text)

# Try to call publish tool
publish_payload = {
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
        "name": "publish_note",
        "arguments": {
            "title": "天界山一日游｜云端漫步，把烦恼都踩在脚下",
            "content": "周末逃离城市计划成功！这次打卡了传说中的天界山，真的有种人在画中游的感觉～\n\n🎫 门票福利\n三八节女性只要40元大巴车费（免门票），男性100元！这性价比绝了💰\n\n🚌 交通方式\n可以坐大巴直达山顶，也有自驾的。但山路不好走，技术不行不建议自己开车，大巴更安全省心～\n\n🚶 山顶游玩\n山顶有索道、栈道，老爷顶太高了这次没去挑战😂 有游览车可以坐，山顶绕一圈大概6公里，路比较平坦适合散步，完全不累！\n\n🐐 意外惊喜\n山顶还有散养的山羊！超可爱，拍照很出片📸\n\n☕ 山顶咖啡\n坐在悬崖边，捧着热咖啡看云卷云舒，云海翻涌，远山如黛，这才是生活啊～\n\n💡 小tips：\n- 建议穿舒适的运动鞋\n- 带件薄外套，山顶风大\n- 充电宝必备！美景太多电量消耗快\n- 全程约4-5小时，新手友好\n\n下次想带爸妈一起来，这种不费腿又能看美景的地方，全家出游首选！\n\n#天界山 #周末去哪儿 #户外徒步 #小众景点 #逃离城市计划 #河南旅游 #山顶风光",
            "images": [
                "img_v3_02vn_0e558962-964d-4049-aabf-bef148753e3g",
                "img_v3_02vn_c9abc0cb-aea2-4b07-aa61-bd391825fbfg",
                "img_v3_02vn_b07c61db-ed23-4181-b681-e7aa5817317g",
                "img_v3_02vn_cf39ee63-d50f-4551-a938-b16128935e6g"
            ]
        }
    },
    "id": 3
}
response = requests.post(url, json=publish_payload)
print("Publish response:", response.text)
