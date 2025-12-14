
import os
import sys
import threading
from fastapi import FastAPI, Request, HTTPException
from backend.configs.config_loader import load_config
from backend.core.fb_helper import FacebookClient
from backend.core.schemas import LeadData # Import khuôn dữ liệu
from backend.api.webhook_routes import router as webhook_router
from backend.api.conversation_routes import router as conversation_router
from backend.api.page_config_routes import router as page_config_routes
from backend.api.statistics_routes import router as statistics_routes

from frontend.routes.page_config_routes import router as page_config_frontend_routes
from frontend.routes.conversation_routes import router as conversation_frontend_routes
from dotenv import load_dotenv
load_dotenv() 
from backend.core.redis_client import r


app = FastAPI()

# Gắn router
app.include_router(webhook_router)
app.include_router(conversation_router)
app.include_router(page_config_routes)
app.include_router(page_config_frontend_routes)
app.include_router(conversation_frontend_routes)
app.include_router(statistics_routes)

# VERIFY_TOKEN = os.getenv("FB_VERIFY_TOKEN", "1234567890")
# redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")


# import redis
# import json
# r = redis.from_url(redis_url)

@app.get("/")
def home():
    return {"message": "Chatbot AIHUB is running!", "status": "ok"}


# ---------------------
# Hàm chạy tiến trình song song
# ---------------------
import time
import subprocess

def run_process(command):
    """Chạy 1 command hệ thống song song"""
    proc = subprocess.Popen(command, shell=True)
    return proc

def run_server():
    """Chạy FastAPI server trực tiếp (debug được)"""
    import uvicorn
    uvicorn.run("run:app", host="127.0.0.1", port=int(os.getenv("PORT", 8000)), reload=False)

def start_all_services():
    """Khởi động Uvicorn, Worker và ngrok cùng lúc"""
    print("🚀 Bắt đầu khởi chạy tất cả dịch vụ...")

    # 1. FastAPI server trong thread (debug được)
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()

    time.sleep(3)  # đợi server khởi động

    # 2. Worker
    worker_cmd = "python backend/core/worker.py"
    worker_proc = run_process(worker_cmd)

    time.sleep(1)
    # 3. Ngrok
    ngrok_cmd = "ngrok http {}".format(os.getenv("PORT", "8000"))
    ngrok_proc = run_process(ngrok_cmd)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("⏹ Dừng tất cả tiến trình...")
        worker_proc.terminate()
        ngrok_proc.terminate()
        sys.exit(0)

# ---------------------
# Chạy nếu trực tiếp gọi run.py
# ---------------------
if __name__ == "__main__":
    start_all_services()