from fastapi import APIRouter, Query
import requests
from datetime import datetime

from backend.database.load_pages_config import load_all_fb_tokens

router = APIRouter()


@router.get("/api/conversations")
def get_conversations():
    PAGE_TOKENS = load_all_fb_tokens("backend/configs")
    limit = 100  # tăng limit để giảm số lần gọi API

    conversations_map = {}

    for page_id, ACCESS_TOKEN in PAGE_TOKENS.items():
        if not ACCESS_TOKEN:
            continue

        # URL bắt đầu
        url = f"https://graph.facebook.com/v17.0/{page_id}/conversations"
        params = {
            "access_token": ACCESS_TOKEN,
            "limit": limit,
            "fields": (
                "id,updated_time,link,participants,"
                "messages.limit(1){message,from,created_time}"
            )
        }

        # Loop theo paging.next cho đến khi hết dữ liệu
        while url:
            res = requests.get(url, params=params, timeout=10)
            data = res.json()

            conversations = data.get("data", [])
            url = data.get("paging", {}).get("next")  # trang tiếp theo
            params = None  # Next dùng URL đầy đủ, không cần params nữa

            for conv in conversations:
                conv_id = conv.get("id")

                # Tin nhắn cuối
                last_msg = conv.get("messages", {}).get("data", [])
                if last_msg:
                    m = last_msg[0]
                    message = m.get("message", "")
                    created_time = m.get("created_time", "")
                    fullname = m.get("from", {}).get("name", "Người dùng")
                else:
                    message = ""
                    created_time = ""
                    fullname = "Người dùng"

                # Convert datetime để sort nhanh
                try:
                    dt = datetime.fromisoformat(created_time.replace("Z", "+00:00"))
                except:
                    dt = datetime.min

                conv_key = f"{page_id}_{conv_id}"

                conversations_map[conv_key] = {
                    "conversation_id": conv_id,
                    "page_id": page_id,
                    "fullname": fullname,        # <-- Tên người gửi tin nhắn cuối
                    "last_message": message,
                    "last_message_time": created_time,
                    "last_message_dt": dt
                }

    # Convert dict → list
    all_conversations = list(conversations_map.values())

    # Sort theo thời gian giảm dần
    all_conversations.sort(key=lambda x: x["last_message_dt"], reverse=True)

    return {
        "success": True,
        "total": len(all_conversations),
        "conversations": all_conversations,
        "page_ids": list(PAGE_TOKENS.keys())
    }

@router.get("/api/conversations/{conversation_id}")
def get_conversation_details(
    conversation_id: str,
    page_id: str = Query(..., description="ID fanpage để lấy access_token")
):
    PAGE_TOKENS = load_all_fb_tokens("backend/configs")
    ACCESS_TOKEN = PAGE_TOKENS.get(page_id)

    if not ACCESS_TOKEN:
        return {"success": False, "error": "Page ID không có token hợp lệ."}

    all_messages = []
    
    # URL ban đầu
    url = f"https://graph.facebook.com/v17.0/{conversation_id}"
    params = {
        "access_token": ACCESS_TOKEN,
        "fields": (
            "id,participants,"
            "messages.limit(50){id,message,from,created_time}"
        )
    }

    # Lặp phân trang theo cursor
    while True:
        res = requests.get(url, params=params, timeout=10)
        data = res.json()

        # Lấy danh sách tin nhắn
        msgs = data.get("messages", {}).get("data", [])
        all_messages.extend(msgs)

        # Kiểm tra next page
        paging = data.get("messages", {}).get("paging", {})
        next_url = paging.get("next")

        if not next_url:
            break

        # next_url đã chứa đủ query → params phải None
        url = next_url
        params = None

    # Sort tin nhắn theo thời gian
    all_messages.sort(key=lambda x: x["created_time"])

    # Lấy danh sách participants
    participants = data.get("participants", {}).get("data", [])

    return {
        "success": True,
        "conversation_id": conversation_id,
        "page_id": page_id,
        "participants": participants,
        "total_messages": len(all_messages),
        "messages": all_messages
    }
