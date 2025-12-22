# backend/api/webhook_routes.py
import json
from fastapi import APIRouter, Request, HTTPException, Response
import httpx
from backend.core import redis_client
from backend.core.schemas import LeadData
import redis
import os
from fastapi.responses import PlainTextResponse
from dotenv import load_dotenv
load_dotenv()
# Khởi tạo Redis
redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
r = redis.from_url(redis_url)

# Lấy VERIFY_TOKEN
VERIFY_TOKEN = os.getenv("FB_VERIFY_TOKEN", "1234567890")
ASP_CORE_URL = os.getenv("API_FB_WEBHOOK_URL", "https://localhost:7275/api/chatbot/fb-webhook")

router = APIRouter()
from backend.core.crm_connector import CRMConnector

crm = CRMConnector()

def _verify_webhook(request: Request):
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        print("WEBHOOK_VERIFIED")
        return PlainTextResponse(content=challenge)
    return PlainTextResponse(content="Forbidden", status_code=403)

# Route với slash cuối
@router.get("/webhook/")
def verify_webhook_slash(request: Request):
    return _verify_webhook(request)

# Route không slash, tránh redirect
@router.get("/webhook", include_in_schema=False)
def verify_webhook_noslash(request: Request):
    return _verify_webhook(request)

async def is_endpoint_alive(url: str, timeout: float = 1.0) -> bool:
    try:
        async with httpx.AsyncClient(
            timeout=timeout,
            verify=False
        ) as client:
            response = await client.get(url)
            return response.status_code < 500
    except Exception:
        return False

@router.post("/webhook")
async def handle_webhook(request: Request):
    try:
        print("🌟 Đã nhận webhook từ Facebook")
        body = await request.json()
        r.rpush("chat_queue", json.dumps(body))
        # if ASP_CORE_URL:
        #     alive = await is_endpoint_alive(ASP_CORE_URL)
        #     if alive:
        #         try:
        #             async with httpx.AsyncClient(
        #                 timeout=3,
        #                 verify=False
        #             ) as client:
        #                 await client.post(ASP_CORE_URL, json=body)
        #         except Exception as e:
        #             print("⚠️ ASP.NET Core gọi thất bại, bỏ qua:", e)
        #     else:
        #         print("⚠️ ASP.NET Core không hoạt động, skip gọi")

        # async with httpx.AsyncClient(verify=False) as client:
        #     try:
        #         await client.post(ASP_CORE_URL, json=body)
        #     except Exception as e:
        #         import traceback
        #         print("❌ Error calling ASP.NET Core:")
        #         traceback.print_exc()
    except Exception as e:
        print("❌ Webhook error:", e)
    return Response(status_code=200)

# def extract_lead_from_fb(body: dict):
#     try:
#         entry = body["entry"][0]
#         messaging = entry["messaging"][0]
#         sender_id = messaging["sender"]["id"]
#         text = messaging.get("message", {}).get("text", "")
#         return {
#             "facebook_id": sender_id,
#             "phone": None,          # chưa có
#             "full_name": None,
#             "message": text,
#             "source": "facebook"
#         }
#     except Exception as e:
#         print("❌ Không parse được lead:", e)
#         return None

# @router.post("/mock-crm/leads")
# async def receive_lead_from_bot(lead: LeadData):
#     print("\n----------------------------------------")
#     print("🌟 [MOCK CRM] ĐÃ NHẬN ĐƯỢC DEAL MỚI!")
#     print(f"👤 Khách hàng: {lead.full_name}")
#     print(f"📞 SĐT: {lead.phone} | 📧 Email: {lead.email}")
#     print(f"🎯 Intent: {lead.intent}")
#     print(f"📊 Phân loại: {lead.classification}")
#     print(f"💯 Lead Score: {lead.score}/100")
#     print(f"📝 Ghi chú AI: {lead.notes}")
#     print("----------------------------------------\n")
    
#     return {
#         "status": "success",
#         "message": "Lead created successfully",
#         "deal_id": "DEAL_NEW_9999"
#     }
