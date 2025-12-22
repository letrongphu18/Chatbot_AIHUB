print("[WORKER] STARTED")

import os
import sys


BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, BASE_DIR)

from backend.database.session import SessionLocal
from sqlalchemy.orm import Session

# sys.path.insert(0, os.path.abspath("."))
# sys.path.append(os.getcwd())
import datetime
import time
import redis
import json
from dotenv import load_dotenv

#from backend.configs.config_loader import load_config
from backend.core.ai_engine import generate_ai_response
from backend.core.flow_engine import FlowEngine
from backend.core.fb_helper import FacebookClient
from backend.core.crm_connector import CRMConnector
from backend.database import crud
HANDOFF_TIMEOUT_SECONDS = 600
load_dotenv()

# ----------------------
# Kiểm tra Redis và Google API Key
# ----------------------
redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
redis_client = redis.from_url(redis_url)

try:
    redis_client.ping()
except redis.exceptions.ConnectionError:
    print("❌ Redis chưa sẵn sàng. Thử lại sau 5s...")
    time.sleep(5)
    sys.exit(1)

if not os.getenv("GOOGLE_API_KEY"):
    print("❌ Chưa cấu hình GOOGLE_API_KEY")
    sys.exit(1)


flow_engine = FlowEngine(redis_client)

# fb_tokens = crud.load_all_fb_tokens()    
# fb_client = FacebookClient(page_tokens=fb_tokens)
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
    ĐÃ CẬP NHẬT để lấy các trường Handoff
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

    # <<< XỬ LÝ TRƯỜNG HANDOFF >>>
    session["conversation_mode"] = session.get("conversation_mode", "BOT")
    try:
        # last_human_activity phải là float (timestamp)
        session["last_human_activity"] = float(session.get("last_human_activity", 0))
    except:
        session["last_human_activity"] = 0
    # <<< KẾT THÚC XỬ LÝ TRƯỜNG HANDOFF >>>
        
    return session

def update_session(sender_id, page_id, topic, state, new_data=None, 
                   conversation_mode=None, last_human_activity=None): # <<< THÊM THAM SỐ HANDOFF
    """
    Lưu Session chuẩn Schema
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

    # <<< THÊM CÁC TRƯỜNG HANDOFF VÀO PAYLOAD >>>
    if conversation_mode:
        update_payload["conversation_mode"] = conversation_mode
    if last_human_activity is not None:
        update_payload["last_human_activity"] = str(last_human_activity) # Lưu dưới dạng string
    # <<< KẾT THÚC THÊM CÁC TRƯỜNG HANDOFF >>>

    # 4. Lưu vào Redis
    redis_client.hset(key, mapping=update_payload)
    redis_client.expire(key, 86400 * 3) # 


def process_message():
    print(" Worker: Bắt đầu xử lý tin nhắn từ chat_queue...")
    with SessionLocal() as db:
        fb_tokens = crud.load_all_fb_tokens(db)
    fb_client = FacebookClient(page_tokens=fb_tokens)
    while True:
        # db = SessionLocal()
        # try:
        #     db.close()
        # except:
        #     pass
        
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

                    # 1. Load Config (Topic Pack)
                    #config = load_config(page_id)
                    #config = get_page_config_by_id("backend/configs",page_id)
                    #config = crud.get_config_by_page_id(page_id)
                    with SessionLocal() as db:
                        config = crud.get_config_by_page_id(db, page_id)
                    if not config:
                        print("❌ Không tìm thấy Config")
                        continue
                    
                    page_name = config.get("page_name")
                    if not page_name:
                        page_name = config.get("meta_data", {}).get("brand_default", "Unknown")
                    config["page_name"] = page_name
                    topic_id = config.get("topic_id", "general")

                    # 2. LOAD SESSION & HISTORY
                    history = get_chat_history(sender_id)
                    current_history = history + [{"role": "user", "content": message_text}]

                    session_obj = get_session(sender_id)
                    # Lấy trạng thái Handoff
                    mode = session_obj.get("conversation_mode", "BOT")
                    last_human_activity = session_obj.get("last_human_activity", 0)
                    current_time = time.time()
                    
                    current_state = session_obj.get("state", "START")
                    session_data_json = session_obj.get("data", {}) 

                #   human  logic
                    if message_text.upper().startswith("!TAKEOVER"):
                        mode = "HUMAN"
                        print(f"[{sender_id}] *** ADMIN đã tiếp quản hội thoại ***")
                        
                        
                        update_session(sender_id, page_id, topic_id, current_state, new_data=None, 
                                    conversation_mode=mode, last_human_activity=current_time)
                        try:
                            fb_client.send_text_message(sender_id, "Bot đã chuyển sang chế độ hỗ trợ của Admin. Vui lòng đợi phản hồi.", page_id=page_id)
                        except Exception as e:
                            print(f"❌ Lỗi gửi FB: {e}")
                            continue  # hoặc log, nhưng không crash

                        #fb_client.send_text_message(sender_id, "Bot đã chuyển sang chế độ hỗ trợ của Admin. Vui lòng đợi phản hồi.", page_id=page_id)
                        continue 

                    
                    if mode == "HUMAN":
                        
                        if current_time - last_human_activity > HANDOFF_TIMEOUT_SECONDS:
                            print(f"[{sender_id}] Admin timeout. Chuyển quyền xử lý về BOT.")
                            mode = "BOT" # Reset mode
                            
                            fb_client.send_text_message(sender_id, "Admin đang bận. Bot sẽ tiếp tục hỗ trợ bạn.", page_id=page_id)
                            
                        else:
                            
                            print(f"[{sender_id}] Đang ở chế độ HUMAN. Bot tạm dừng.")
                            
                            update_session(sender_id, page_id, topic_id, current_state, new_data=None, 
                                        conversation_mode=mode, last_human_activity=current_time)
                            continue 

                   
                    update_session(sender_id, page_id, topic_id, current_state, new_data=None, 
                                conversation_mode=mode, last_human_activity=current_time)
                  
                    if mode == "BOT":
                        
                     
                        ai_json = generate_ai_response(current_history, config, json.dumps(session_data_json))
                        print("AI response:", ai_json)
                        
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
                            new_data=new_data_points,
                            conversation_mode=mode,
                            last_human_activity=current_time
                        )

                   
                        print(f" Trả lời: {list(fb_tokens.keys())}...")
                        fb_client.send_text_message(sender_id, reply_text, page_id=page_id)
                        save_chat_history(sender_id, "user", message_text)
                        save_chat_history(sender_id, "model", reply_text)

                        # 7. Push CRM (Nếu đủ điều kiện)
                        if final_result["action"] == "PUSH_CRM":
                            print(f" DATA LEAD -> CRM...")
                            lead_data["page_id"] = page_id
                            crm.push_lead(lead_data)
                    
                   

        except Exception as e:
            print(f" Worker Lỗi: {e}")
            import traceback
            traceback.print_exc()
            if "mysql" in str(e).lower() or "connection" in str(e).lower():
                print(" Lỗi DB! Đợi 5s trước khi retry...")
                time.sleep(5)
            else:
                time.sleep(1)

if __name__ == "__main__":
    process_message()