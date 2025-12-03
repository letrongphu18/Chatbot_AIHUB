
import os
import sys
import datetime

sys.path.append(os.getcwd())

import redis
import json
import time
from dotenv import load_dotenv

from backend.configs.config_loader import load_config
from backend.core.ai_engine import generate_ai_response
from backend.core.flow_engine import FlowEngine
from backend.core.fb_helper import FacebookClient
from backend.core.crm_connector import CRMConnector


load_dotenv()
redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
redis_client = redis.from_url(redis_url)

flow_engine = FlowEngine(redis_client)
from backend.database.load_pages_config import load_all_fb_tokens
fb_tokens = load_all_fb_tokens("backend/configs")  # Trả về dict {page_id: FB_PAGE_ACCESS_TOKEN}
fb_client = FacebookClient(page_tokens=fb_tokens)
#fb_client = FacebookClient()
crm = CRMConnector()

print(" WORKER ĐANG CHẠY... ")


def get_chat_history(sender_id):
    """Lấy lịch sử chat (Short-term memory)"""
    key = f"history:{sender_id}"
    raw_list = redis_client.lrange(key, -10, -1) 
    history = []
    for item in raw_list:
        try:
            history.append(json.loads(item))
        except:
            pass
    return history

def save_chat_history(sender_id, role, content):
    """Lưu tin nhắn mới"""
    key = f"history:{sender_id}"
    message = json.dumps({"role": role, "content": content})
    redis_client.rpush(key, message)
    redis_client.ltrim(key, -50, -1)

def get_session(sender_id):
    """
    Lấy toàn bộ Context của khách hàng từ Redis
    """
    key = f"session:{sender_id}"
    data = redis_client.hgetall(key)
    
    # Convert bytes sang string/dict
    session = {k.decode(): v.decode() for k, v in data.items()}
    
    # Parse field 'data' từ JSON string sang Dict
    if "data" in session:
        try:
            session["data"] = json.loads(session["data"])
        except:
            session["data"] = {}
    else:
        session["data"] = {}
        
    return session

def update_session(sender_id, page_id, topic, state, new_data=None):
    """
    Lưu Session chuẩn Schema:
    - user_id, page_id, topic, state, data (JSON), updated_at
    """
    key = f"session:{sender_id}"
    
    # 1. Lấy data JSON cũ để merge (tránh mất dữ liệu cũ)
    current_data_str = redis_client.hget(key, "data")
    current_data = json.loads(current_data_str) if current_data_str else {}
    
    # 2. Cập nhật data mới 
    if new_data:
        current_data.update(new_data)
    
    # 3. Chuẩn bị Payload
    update_payload = {
        "user_id": sender_id,
        "page_id": page_id,
        "topic": topic,
        "state": state,
        "data": json.dumps(current_data), # Lưu dưới dạng JSON String
        "updated_at": datetime.datetime.now().isoformat()
    }

    # 4. Lưu vào Redis
    redis_client.hset(key, mapping=update_payload)
    redis_client.expire(key, 86400 * 3) # 

def process_message():
    while True:
        try:
            packed_item = redis_client.blpop("chat_queue", timeout=5)
            if not packed_item: continue 

            raw_json = packed_item[1]
            body = json.loads(raw_json)

            for entry in body.get("entry", []):
                page_id = entry.get("id") 
                for messaging in entry.get("messaging", []):
                    sender_id = messaging.get("sender", {}).get("id")
                    message_text = messaging.get("message", {}).get("text")

                    if not message_text: continue

                    print(f"\n📨 User {sender_id}: {message_text}")

                    # 1. Load Config (Topic Pack)
                    config = load_config(page_id)
                    if not config:
                        print("❌ Không tìm thấy Config")
                        continue
                    
           
                    page_name = config.get("page_name")
                    if not page_name:
                        page_name = config.get("meta_data", {}).get("brand_default", "Unknown")
                    config["page_name"] = page_name
                    topic_id = config.get("topic_id", "general")

                    
                    history = get_chat_history(sender_id)
                    current_history = history + [{"role": "user", "content": message_text}]

             
                    session_obj = get_session(sender_id)
                    current_state = session_obj.get("state", "START")
                    session_data_json = session_obj.get("data", {}) # Đây là cái cục {cig_per_day: 10...}

             
                    ai_json = generate_ai_response(current_history, config, json.dumps(session_data_json))
                    
            
                    final_result = flow_engine.process_ai_result(sender_id, message_text, ai_json, config)
                    reply_text = final_result["text_to_send"]
                    lead_data = final_result["lead_data"]

               
                    next_state = ai_json.get("next_state") or current_state
                    
               
                    new_data_points = {}
                    if lead_data.get("classification"):
                        new_data_points["classification"] = lead_data.get("classification")
                    if lead_data.get("subtopic"):
                        new_data_points["subtopic"] = lead_data.get("subtopic")
                   
                    
                    update_session(
                        sender_id=sender_id,
                        page_id=page_id,
                        topic=topic_id,
                        state=next_state,
                        new_data=new_data_points
                    )

                    # Gửi tin & Lưu lịch sử chat
                    print(f" 🤖 Trả lời: {list(fb_tokens.keys())}...")
                    fb_client.send_text_message(sender_id, reply_text, page_id=page_id)
                    save_chat_history(sender_id, "user", message_text)
                    save_chat_history(sender_id, "model", reply_text)

                    # 7. Push CRM (Nếu đủ điều kiện)
                    if final_result["action"] == "PUSH_CRM":
                        print(f" DATA LEAD -> CRM...")
                        crm.push_lead(lead_data)

        except Exception as e:
            print(f" Worker Lỗi: {e}")
            time.sleep(1)

if __name__ == "__main__":
    process_message()