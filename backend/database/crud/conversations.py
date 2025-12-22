from datetime import datetime
import requests
from sqlalchemy.orm import Session

from backend.database.models.lead_data import LeadData
from backend.database import crud


from datetime import datetime
import requests
from sqlalchemy.orm import Session
from backend.database import crud


def get_conversations(db: Session):
    PAGE_TOKENS = crud.load_all_fb_tokens(db)
    limit = 100
    conversations_map = {}

    has_success_connection = False
    errors = []

    for page_id, ACCESS_TOKEN in PAGE_TOKENS.items():
        if not ACCESS_TOKEN:
            errors.append(f"Page {page_id}: missing access token")
            continue

        url = f"https://graph.facebook.com/v17.0/{page_id}/conversations"
        params = {
            "access_token": ACCESS_TOKEN,
            "limit": limit,
            "fields": (
                "id,updated_time,link,"
                "participants{id,name},"
                "messages.limit(1){message,from,created_time}"
            )
        }

        while url:
            try:
                res = requests.get(url, params=params, timeout=10)
                if res.status_code != 200:
                    errors.append(
                        f"Page {page_id}: HTTP {res.status_code} - {res.text}"
                    )
                    break

                data = res.json()
                if "error" in data:
                    errors.append(
                        f"Page {page_id}: {data['error'].get('message')}"
                    )
                    break

                conversations = data.get("data", [])
                if conversations:
                    has_success_connection = True

                # paging
                url = data.get("paging", {}).get("next")
                params = None

                for conv in conversations:
                    conv_id = conv.get("id")
                    link = conv.get("link", "")

                    # ===== LẤY USER (PSID) TỪ PARTICIPANTS =====
                    participants = conv.get("participants", {}).get("data", [])
                    sender_id = None
                    fullname = "Người dùng"

                    for p in participants:
                        if p.get("id") != page_id:
                            sender_id = p.get("id")
                            fullname = p.get("name", fullname)
                            break

                    # ===== LAST MESSAGE =====
                    last_msg = conv.get("messages", {}).get("data", [])
                    if last_msg:
                        m = last_msg[0]
                        message = m.get("message", "")
                        created_time = m.get("created_time", "")
                    else:
                        message = ""
                        created_time = ""

                    try:
                        dt = datetime.fromisoformat(
                            created_time.replace("Z", "+00:00")
                        )
                    except Exception:
                        dt = datetime.min

                    conv_key = f"{page_id}_{conv_id}"

                    conversations_map[conv_key] = {
                        "conversation_id": conv_id,
                        "page_id": page_id,
                        "channel_id": page_id,

                        # 🔑 QUAN TRỌNG
                        "sender_id": sender_id,
                        "facebook_uid": sender_id,

                        "fanpage_name": crud.get_page_name_by_id(
                            page_id, ACCESS_TOKEN
                        ),
                        "link": link,
                        "fullname": fullname,

                        # CRM placeholders
                        "customer_name": fullname,
                        "phone": get_phone_by_facebook_uid(
                            db, sender_id, page_id),
                        "email": get_email_by_facebook_uid(
                            db, sender_id, page_id),
                        "tags": "",
                        "last_message": message,
                        "last_message_time": created_time,
                        "last_message_dt": dt
                    }

            except Exception as e:
                errors.append(f"Page {page_id}: exception {str(e)}")
                break

    all_conversations = list(conversations_map.values())
    all_conversations.sort(
        key=lambda x: x["last_message_dt"], reverse=True
    )

    return {
        "success": has_success_connection,
        "conversations": all_conversations,
        "error_count": len(errors),
        "errors": errors
    }

def get_phone_by_facebook_uid(db: Session, facebook_uid: str, page_id: str):
    try:
        # Lấy số điện thoại cuối cùng từ lead có facebook_uid và page_id tương ứng
        lead = db.query(LeadData).filter(
            LeadData.facebook_uid == facebook_uid,  
            LeadData.page_id == page_id,
            LeadData.phone != None
        ).order_by(LeadData.id.desc()).first()
        if lead:
            return lead.phone
        return None
    except Exception as e:
        print("❌ LỖI LẤY SỐ ĐIỆN THOẠI THEO FACEBOOK UID:", repr(e))
        raise
def get_email_by_facebook_uid(db: Session, facebook_uid: str, page_id: str):
    try:
        # Lấy email cuối cùng từ lead có facebook_uid và page_id tương ứng
        lead = db.query(LeadData).filter(
            LeadData.facebook_uid == facebook_uid,  
            LeadData.page_id == page_id,
            LeadData.email != None
        ).order_by(LeadData.id.desc()).first()
        if lead:
            return lead.email
        return None
    except Exception as e:
        print("❌ LỖI LẤY EMAIL THEO FACEBOOK UID:", repr(e))
        raise