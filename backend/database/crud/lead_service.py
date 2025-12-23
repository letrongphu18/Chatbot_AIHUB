from backend.database.models.lead_data import LeadData
from backend.core.schemas import LeadData as LeadDataSchema
import requests
from sqlalchemy.orm import Session
from backend.database.session import SessionLocal
# =========================
# CÁC FIELD CUSTOMER CHO PHÉP
# =========================

def apply_lead_schema(lead: LeadData, s: LeadDataSchema):
    if s.phone is not None:
        lead.phone = s.phone

    if s.email is not None:
        lead.email = s.email

    if s.full_name:
        lead.full_name = s.full_name

    if s.facebook_uid:
        lead.facebook_uid = s.facebook_uid

    if s.page_id:
        lead.page_id = s.page_id

    if s.profile_link:
        lead.profile_link = s.profile_link

    if s.topic:
        lead.topic = s.topic

    if s.subtopic:
        lead.subtopic = s.subtopic

    if s.intent:
        lead.intent = s.intent

    if s.classification:
        lead.classification = s.classification

    if s.stage:
        lead.stage = s.stage

    if s.tags:
        lead.tags = s.tags

    if s.score is not None:
        lead.score = s.score

    if s.lead_source:
        lead.lead_source = s.lead_source

    if s.source_page:
        lead.source_page = s.source_page

    if s.channel:
        lead.channel = s.channel

    if s.notes:
        lead.notes = s.notes

def save_lead_to_db(db: Session,lead_data: dict):
    try:
        phone = lead_data.get("phone")
        email = lead_data.get("email")
        facebook_uid = lead_data.get("facebook_uid")
        page_id = lead_data.get("page_id")
        # 1. Ưu tiên identity theo channel
        lead = db.query(LeadData).filter(
            LeadData.facebook_uid == facebook_uid,
            LeadData.page_id == page_id
        ).first()

        # 2. Nếu chưa có lead channel → thử merge global
        if not lead and phone:
            lead = db.query(LeadData).filter(LeadData.phone == phone).first()

        if not lead and email:
            lead = db.query(LeadData).filter(LeadData.email == email).first()
        
        if not lead:
            #lead = LeadData(phone=phone)
            lead = LeadData()
            db.add(lead)
        apply_lead_schema(lead, LeadDataSchema(**lead_data))
        
        db.commit()
        db.refresh(lead)
        return lead.id
    except Exception as e:
        db.rollback()
        print("❌ LỖI LƯU CUSTOMER:", repr(e))
        raise

    # finally:
    #     db.close()

def get_leads_by_facebook_uid(db: Session, facebook_uid: str, page_id: str):
    try:
        lead = db.query(LeadData).filter(
            LeadData.facebook_uid == facebook_uid,
            LeadData.page_id == page_id
        ).order_by(LeadData.id.desc()).first()
        if lead:
            return lead
        return LeadData()
    except Exception as e:
        print("❌ LỖI LẤY LEAD THEO FACEBOOK UID:", repr(e))
        raise



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

