#!/usr/bin/env python3
"""
Feishu Image Sender
Send images to Feishu (Lark) via webhook or Bot API
"""

import requests
import base64
import json
import os
from typing import Optional


def get_tenant_access_token(app_id: str, app_secret: str) -> str:
    """
    Get tenant_access_token from Feishu API
    
    Args:
        app_id: Feishu app ID
        app_secret: Feishu app secret
        
    Returns:
        tenant_access_token string
    """
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    headers = {"Content-Type": "application/json"}
    data = {
        "app_id": app_id,
        "app_secret": app_secret
    }
    
    response = requests.post(url, headers=headers, json=data)
    result = response.json()
    
    if result.get("code") == 0:
        return result.get("tenant_access_token")
    else:
        raise Exception(f"Failed to get token: {result}")


def upload_image_to_feishu(
    image_path: str,
    tenant_access_token: str
) -> str:
    """
    Upload image to Feishu and get image_key
    
    Args:
        image_path: Local path to image file
        tenant_access_token: Feishu tenant access token
        
    Returns:
        image_key for sending messages
    """
    url = "https://open.feishu.cn/open-apis/im/v1/images"
    headers = {
        "Authorization": f"Bearer {tenant_access_token}"
    }
    
    with open(image_path, "rb") as f:
        files = {"image": f}
        data = {"image_type": "message"}
        response = requests.post(url, headers=headers, files=files, data=data)
    
    result = response.json()
    
    if result.get("code") == 0:
        return result.get("data", {}).get("image_key")
    else:
        raise Exception(f"Failed to upload image: {result}")


def send_image_via_webhook(
    image_path: str,
    webhook_url: str
) -> dict:
    """
    Send image via Feishu webhook
    
    Args:
        image_path: Local path to image file
        webhook_url: Feishu webhook URL
        
    Returns:
        API response dict
    """
    # Read image and encode as base64
    with open(image_path, "rb") as f:
        image_data = f.read()
    
    image_base64 = base64.b64encode(image_data).decode("utf-8")
    
    # Prepare webhook payload
    payload = {
        "msg_type": "image",
        "content": {
            "image_key": image_base64  # Webhook accepts base64 directly
        }
    }
    
    # Send request
    headers = {"Content-Type": "application/json"}
    response = requests.post(webhook_url, headers=headers, json=payload)
    
    return response.json()


def send_image_via_bot_api(
    image_path: str,
    chat_id: str,
    tenant_access_token: str
) -> dict:
    """
    Send image via Feishu Bot API
    
    Args:
        image_path: Local path to image file
        chat_id: Feishu chat ID
        tenant_access_token: Feishu tenant access token
        
    Returns:
        API response dict
    """
    # First upload image to get image_key
    image_key = upload_image_to_feishu(image_path, tenant_access_token)
    
    # Send message with image
    url = "https://open.feishu.cn/open-apis/im/v1/messages"
    headers = {
        "Authorization": f"Bearer {tenant_access_token}",
        "Content-Type": "application/json"
    }
    params = {"receive_id_type": "chat_id"}
    
    content = json.dumps({
        "image_key": image_key
    })
    
    data = {
        "receive_id": chat_id,
        "msg_type": "image",
        "content": content
    }
    
    response = requests.post(url, headers=headers, params=params, json=data)
    return response.json()


def send_image_to_feishu(
    image_path: str,
    webhook_url: Optional[str] = None,
    chat_id: Optional[str] = None,
    tenant_access_token: Optional[str] = None,
    app_id: Optional[str] = None,
    app_secret: Optional[str] = None
) -> dict:
    """
    Send an image to Feishu
    
    Supports two methods:
    1. Webhook: Provide webhook_url
    2. Bot API: Provide chat_id + (tenant_access_token OR app_id + app_secret)
    
    Args:
        image_path: Local path to image file
        webhook_url: Feishu webhook URL (for webhook method)
        chat_id: Feishu chat ID (for bot API method)
        tenant_access_token: Feishu tenant access token (for bot API method)
        app_id: Feishu app ID (alternative to tenant_access_token)
        app_secret: Feishu app secret (alternative to tenant_access_token)
        
    Returns:
        API response dict
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found: {image_path}")
    
    # Method 1: Webhook
    if webhook_url:
        return send_image_via_webhook(image_path, webhook_url)
    
    # Method 2: Bot API
    if chat_id:
        # Get token if not provided
        if not tenant_access_token:
            if not app_id or not app_secret:
                raise ValueError("Either tenant_access_token or (app_id + app_secret) required")
            tenant_access_token = get_tenant_access_token(app_id, app_secret)
        
        return send_image_via_bot_api(image_path, chat_id, tenant_access_token)
    
    raise ValueError("Either webhook_url or chat_id must be provided")


def send_text_to_feishu(
    text: str,
    webhook_url: Optional[str] = None,
    chat_id: Optional[str] = None,
    tenant_access_token: Optional[str] = None
) -> dict:
    """
    Send text message to Feishu
    
    Args:
        text: Message text
        webhook_url: Feishu webhook URL
        chat_id: Feishu chat ID (requires tenant_access_token)
        tenant_access_token: Feishu tenant access token
        
    Returns:
        API response dict
    """
    if webhook_url:
        payload = {
            "msg_type": "text",
            "content": {"text": text}
        }
        headers = {"Content-Type": "application/json"}
        response = requests.post(webhook_url, headers=headers, json=payload)
        return response.json()
    
    elif chat_id and tenant_access_token:
        url = "https://open.feishu.cn/open-apis/im/v1/messages"
        headers = {
            "Authorization": f"Bearer {tenant_access_token}",
            "Content-Type": "application/json"
        }
        params = {"receive_id_type": "chat_id"}
        
        content = json.dumps({"text": text})
        data = {
            "receive_id": chat_id,
            "msg_type": "text",
            "content": content
        }
        
        response = requests.post(url, headers=headers, params=params, json=data)
        return response.json()
    
    else:
        raise ValueError("Either webhook_url or (chat_id + tenant_access_token) required")


if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python feishu_image_sender.py <image_path> [webhook_url]")
        sys.exit(1)
    
    image_path = sys.argv[1]
    webhook_url = sys.argv[2] if len(sys.argv) > 2 else None
    
    if webhook_url:
        result = send_image_to_feishu(image_path, webhook_url=webhook_url)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print("Please provide webhook_url or set up Bot API credentials")
