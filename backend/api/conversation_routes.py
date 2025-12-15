from fastapi import APIRouter, Query
import requests
from datetime import datetime
from fastapi import Depends
from backend.auth.api_key_auth import check_api_key
from backend.database.crud import load_all_fb_tokens
from backend.database import crud
from backend.database.session import SessionLocal
router = APIRouter(dependencies=[Depends(check_api_key)])

# Dependency để lấy DB session

@router.get("/api/conversations")
def get_conversations():
    PAGE_TOKENS = crud.load_all_fb_tokens()
    limit = 100  
    conversations_map = {}
    for page_id, ACCESS_TOKEN in PAGE_TOKENS.items():
        if not ACCESS_TOKEN:
            continue
        url = f"https://graph.facebook.com/v17.0/{page_id}/conversations"
        params = {
            "access_token": ACCESS_TOKEN,
            "limit": limit,
            "fields": (
                "id,updated_time,link,participants,"
                "messages.limit(1){message,from,created_time}"
            )
        }
        while url:
            res = requests.get(url, params=params, timeout=10)
            data = res.json()

            conversations = data.get("data", [])
            url = data.get("paging", {}).get("next")  
            params = None 

            for conv in conversations:
                conv_id = conv.get("id")
                link = conv.get("link", "")
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
                try:
                    dt = datetime.fromisoformat(created_time.replace("Z", "+00:00"))
                except:
                    dt = datetime.min
                conv_key = f"{page_id}_{conv_id}"
                conversations_map[conv_key] = {
                    "conversation_id": conv_id,
                    "page_id": page_id,
                    "fanpage_name": crud.get_page_name_by_id(page_id, ACCESS_TOKEN),
                    "link": link,
                    "fullname": fullname,        # <-- Tên người gửi tin nhắn cuối
                    "customer_name": "",
                    "phone": "",
                    "email": "",
                    "tags": "",
                    "last_message": message, # tin nhắn cuối
                    "last_message_time": created_time,
                    "last_message_dt": dt
                }
    all_conversations = list(conversations_map.values())
    all_conversations.sort(key=lambda x: x["last_message_dt"], reverse=True)
    return {
        "success": True,
        "conversations": all_conversations
    }

@router.get("/api/conversation/{conversation_id}")
def get_conversation_details(
    conversation_id: str,
    page_id: str = Query(..., description="ID fanpage để lấy access_token"),
):

    ACCESS_TOKEN = crud.get_token_by_page_id(page_id)
    
    if not ACCESS_TOKEN:
        return {"success": False, "error": "Page ID không có token hợp lệ."}
    all_messages = []
    url = f"https://graph.facebook.com/v17.0/{conversation_id}"
    params = {
        "access_token": ACCESS_TOKEN,
        "fields": (
            "id,participants,"
            "messages.limit(50){id,message,from,created_time}"
        )
    }
    while True:
        res = requests.get(url, params=params, timeout=10)
        data = res.json()
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
        "fanpage_name": crud.get_page_name_by_id(page_id, ACCESS_TOKEN),
        "customer_name": "",
        "phone": "",
        "email": "",
        "address": "",
        "email": "",
        "customer_needs": "",
        "messages": all_messages
    }
