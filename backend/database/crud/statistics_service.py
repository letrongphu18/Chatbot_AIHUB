import requests
from backend.database import crud
from backend.database.models.lead_data import LeadData
from backend.database.models.page_config import Channel
from backend.database.session import SessionLocal

def get_db_instance():
    db = SessionLocal()
    try:
        return db
    except:
        db.rollback() 
        raise
    finally:
        pass 
db = get_db_instance()


def get_statistics():
    try:
        conversations = count_conversations().get("total_conversations", 0)
        fanpage = db.query(Channel).filter().count()
        leads_ = db.query(LeadData).filter()
        # leads_new = db.query(LeadData).filter(LeadData.status == "new").count()
        # pending_leads = db.query(LeadData).filter(LeadData.status == "pending").count()
        # completed_leads = db.query(LeadData).filter(LeadData.status == "completed").count()

        return {
            "conversations": conversations,
            "fanpages": fanpage,
            "leads_new": 1,
            "pending_leads": 1,
            "completed_leads": 65,
            "messages_sent": 1000,
            "new_users": 5,
            "active_users": 20,
            "ctr": 0.15,
            "response_rate": 0.85,

        }
    except Exception as e:
        print("❌ LỖI LẤY TẤT CẢ CUSTOMER:", repr(e))
        raise

def count_conversations():
    PAGE_TOKENS = crud.load_all_fb_tokens()
    limit = 100
    total_count = 0

    for page_id, ACCESS_TOKEN in PAGE_TOKENS.items():
        if not ACCESS_TOKEN:
            continue

        url = f"https://graph.facebook.com/v17.0/{page_id}/conversations"
        params = {
            "access_token": ACCESS_TOKEN,
            "limit": limit,
            "fields": "id"  # CHỈ cần id
        }

        while url:
            res = requests.get(url, params=params, timeout=10)
            data = res.json()

            conversations = data.get("data", [])
            total_count += len(conversations)

            url = data.get("paging", {}).get("next")
            params = None  # rất quan trọng khi sang trang

    return {
        "success": True,
        "total_conversations": total_count
    }
