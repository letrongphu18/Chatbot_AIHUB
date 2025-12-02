
import os
import sys
from fastapi import FastAPI, Request, HTTPException
from app.config_loader import load_config
from app.fb_helper import FacebookClient
from app.schemas import LeadData # Import khuôn dữ liệu

from dotenv import load_dotenv
load_dotenv() 


app = FastAPI()


#VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "1234567890")
VERIFY_TOKEN = os.getenv("FB_VERIFY_TOKEN", "1234567890")
redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")


import redis
import json
r = redis.from_url(redis_url)

@app.get("/")
def home():
    return {"message": "Chatbot AIHUB is running!", "status": "ok"}

@app.get("/webhook")
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

@app.post("/webhook")
async def handle_webhook(request: Request):
    body = await request.json()
    r.rpush("chat_queue", json.dumps(body))
    return {"message": "Event received"}


@app.post("/mock-crm/leads")
async def receive_lead_from_bot(lead: LeadData):
    """
    Đây là cái túi hứng dữ liệu giả lập.
    """
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