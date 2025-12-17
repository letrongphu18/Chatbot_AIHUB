
import os
import sys
import threading
import time
import subprocess
from dotenv import load_dotenv
load_dotenv() 


#app = create_app()
# ---------------------

from backend.app import create_app

app = create_app()
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