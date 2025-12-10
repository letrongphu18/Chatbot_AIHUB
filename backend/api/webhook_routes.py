# backend/api/webhook_routes.py
import json
from fastapi import APIRouter, Request, HTTPException, Response
import httpx
from backend.core import redis_client
from backend.core.schemas import LeadData
import redis
import os

# Khởi tạo Redis
redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
r = redis.from_url(redis_url)

# Lấy VERIFY_TOKEN
VERIFY_TOKEN = os.getenv("FB_VERIFY_TOKEN", "1234567890")
ASP_CORE_URL = "https://localhost:7275/api/chatbot/fb-webhook"
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
    try:
        body = await request.json()
        r.rpush("chat_queue", json.dumps(body))
        async with httpx.AsyncClient(verify=False) as client:
            try:
                await client.post(ASP_CORE_URL, json=body)
            except Exception as e:
                import traceback
                print("❌ Error calling ASP.NET Core:")
                traceback.print_exc()
    except Exception as e:
        print("❌ Webhook error:", e)
    return Response(status_code=200)

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
