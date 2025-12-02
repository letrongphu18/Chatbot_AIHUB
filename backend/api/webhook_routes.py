# backend/api/webhook_routes.py
import json
from fastapi import APIRouter, Request, HTTPException
from backend.core.schemas import LeadData
import redis
import os

# Khởi tạo Redis
redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
r = redis.from_url(redis_url)

# Lấy VERIFY_TOKEN
VERIFY_TOKEN = os.getenv("FB_VERIFY_TOKEN", "1234567890")

# Tạo router FastAPI
router = APIRouter()

@router.get("/webhook")
def verify_webhook(request: Request):
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if mode and token:
        if mode == "subscribe" and token == VERIFY_TOKEN:
            print("WEBHOOK_VERIFIED")
            return int(challenge)
        else:
            raise HTTPException(status_code=403, detail="Forbidden")
    return {"status": "ok"}

@router.post("/webhook")
async def handle_webhook(request: Request):
    body = await request.json()
    r.rpush("chat_queue", json.dumps(body))
    return {"message": "Event received"}

@router.post("/mock-crm/leads")
async def receive_lead_from_bot(lead: LeadData):
    print("\n----------------------------------------")
    print("🌟 [MOCK CRM] ĐÃ NHẬN ĐƯỢC DEAL MỚI!")
    print(f"👤 Khách hàng: {lead.full_name}")
    print(f"📞 SĐT: {lead.phone} | 📧 Email: {lead.email}")
    print(f"🎯 Intent: {lead.intent}")
    print(f"📊 Phân loại: {lead.classification}")
    print(f"💯 Lead Score: {lead.score}/100")
    print(f"📝 Ghi chú AI: {lead.notes}")
    print("----------------------------------------\n")
    
    return {
        "status": "success",
        "message": "Lead created successfully",
        "deal_id": "DEAL_NEW_9999"
    }
