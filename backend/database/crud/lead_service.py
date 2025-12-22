from backend.database.models.lead_data import LeadData
from backend.database.session import SessionLocal

# =========================
# CÁC FIELD CUSTOMER CHO PHÉP
# =========================
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

def save_lead_to_db(lead_data: dict):
    try:
        phone = lead_data.get("phone")
        lead = db.query(LeadData).filter(LeadData.phone == phone).first()
        is_new = False
        if not lead:
            lead = LeadData(phone=phone)
            db.add(lead)
            is_new = True
        
        # ===== GÁN FIELD RÕ RÀNG =====
        lead.full_name   = lead_data.get("full_name", lead.full_name)
        lead.email       = lead_data.get("email", lead.email)
        lead.page_id     = lead_data.get("page_id", lead.page_id)
        lead.facebook_uid= lead_data.get("facebook_uid", lead.facebook_uid)
        lead.profile_link= lead_data.get("profile_link", lead.profile_link)
        lead.topic       = lead_data.get("topic", lead.topic)
        lead.subtopic    = lead_data.get("subtopic", lead.subtopic)
        lead.tags        = lead_data.get("tags", lead.tags)
        lead.intent      = lead_data.get("intent", lead.intent)
        lead.classification= lead_data.get("classification", lead.classification)
        lead.data_raw    = lead_data.get("data_raw", lead.data_raw)
        lead.score       = lead_data.get("score", lead.score)
        lead.lead_source = lead_data.get("lead_source", lead.lead_source)
        lead.source_page = lead_data.get("source_page", lead.source_page)
        lead.channel     = lead_data.get("channel", lead.channel)
        lead.page_id     = lead_data.get("page_id", lead.page_id)
        lead.conversation_id= lead_data.get("conversation_id", lead.conversation_id)
        lead.notes       = lead_data.get("notes", lead.notes)

        db.commit()
        db.refresh(lead)
        return lead.id
    except Exception as e:
        db.rollback()
        print("❌ LỖI LƯU CUSTOMER:", repr(e))
        raise

    # finally:
    #     db.close()

def get_lead_by_phone(phone: str):
    db = SessionLocal()
    try:
        lead = db.query(LeadData).filter(LeadData.phone == phone).first()
        return lead
    except Exception as e:
        print("❌ LỖI LẤY CUSTOMER THEO SĐT:", repr(e))
        raise

def get_lead_by_id(lead_id: int):
    db = SessionLocal()
    try:
        lead = db.query(LeadData).filter(LeadData.id == lead_id).first()
        return lead
    except Exception as e:
        print("❌ LỖI LẤY CUSTOMER THEO ID:", repr(e))
        raise

def get_all_leads():
    db = SessionLocal()
    try:
        leads = db.query(LeadData).all()
        return leads
    except Exception as e:
        print("❌ LỖI LẤY TẤT CẢ CUSTOMER:", repr(e))
        raise
def delete_lead(lead_id: int):
    db = SessionLocal()
    try:
        lead = db.query(LeadData).filter(LeadData.id == lead_id).first()
        if not lead:
            return False
        db.delete(lead)
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        print("❌ LỖI XÓA CUSTOMER:", repr(e))
        raise

def update_lead(lead_id: int, update_data: dict):
    db = SessionLocal()
    try:
        lead = db.query(LeadData).filter(LeadData.id == lead_id).first()
        if not lead:
            return False
        
        for key, value in update_data.items():
            if hasattr(lead, key):
                setattr(lead, key, value)
        
        db.commit()
        db.refresh(lead)
        return True
    except Exception as e:
        db.rollback()
        print("❌ LỖI CẬP NHẬT CUSTOMER:", repr(e))
        raise

