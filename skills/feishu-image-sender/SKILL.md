---
name: feishu-image-sender
description: |
  Send images to Feishu (Lark) via webhook or bot API. Supports sending local image files, 
  generated images, and screenshots to Feishu chats. Use when user needs to:
  (1) Send images from server to Feishu, (2) Forward screenshots or generated images to Feishu chats,
  (3) Automate image delivery to Feishu channels, (4) Build image notification workflows.
---

# Feishu Image Sender

Send images to Feishu chats from server-side scripts and automation workflows.

## Quick Start

### Send Local Image File

```python
from feishu_image_sender import send_image_to_feishu

# Send to webhook
send_image_to_feishu(
    image_path="/tmp/screenshot.png",
    webhook_url="https://open.feishu.cn/open-apis/bot/v2/hook/xxxxxx"
)

# Send via Bot API (with tenant_access_token)
send_image_to_feishu(
    image_path="/tmp/screenshot.png",
    chat_id="oc_xxxxxx",
    tenant_access_token="t-xxxxxx"
)
```

## Methods

### Method 1: Webhook (Simplest)

Use bot webhook URL for simple integrations:

1. Create a bot in Feishu → Get webhook URL
2. Use `send_image_to_feishu()` with `webhook_url`

### Method 2: Bot API (More Control)

For advanced features (threads, replies, etc.):

1. Get `app_id` and `app_secret` from Feishu app
2. Get `tenant_access_token` via API
3. Use `send_image_to_feishu()` with `chat_id` and `tenant_access_token`

## Scripts

- `scripts/feishu_image_sender.py` - Core image sending functionality

## API Reference

### send_image_to_feishu()

```python
def send_image_to_feishu(
    image_path: str,              # Local path to image file
    webhook_url: str = None,      # Feishu webhook URL
    chat_id: str = None,          # Feishu chat ID (for Bot API)
    tenant_access_token: str = None,  # Bot auth token
    msg_type: str = "image"       # Message type
) -> dict:
    """
    Send an image to Feishu.
    
    Either webhook_url OR (chat_id + tenant_access_token) must be provided.
    
    Returns: API response dict with {'code': 0, 'msg': 'success'} on success
    """
```

## Setup

### Webhook Method

1. In Feishu, add a custom bot to your group
2. Copy the webhook URL
3. Use it directly in the script

### Bot API Method

1. Create a Feishu app at https://open.feishu.cn/app
2. Get `App ID` and `App Secret`
3. Enable bot capabilities
4. Add bot to target chat
5. Get `chat_id` from chat info

## Examples

### Send Screenshot

```python
from feishu_image_sender import send_image_to_feishu

# After capturing screenshot
send_image_to_feishu(
    image_path="/tmp/xhs_qrcode.png",
    webhook_url="https://open.feishu.cn/open-apis/bot/v2/hook/xxxxxxxx"
)
```

### Send with Caption

Images are sent as standalone messages. For text + image, send two messages:

```python
# First send text
send_text_to_feishu("二维码已生成，请扫码登录:", webhook_url=webhook_url)
# Then send image  
send_image_to_feishu("/tmp/qrcode.png", webhook_url=webhook_url)
```
