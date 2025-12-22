import os
import sys
import threading
import time
import subprocess
from dotenv import load_dotenv
load_dotenv() 
from backend.app import create_app

app = create_app()


def run_process(command):
    proc = subprocess.Popen(command, shell=True)
    return proc

def run_server():
    import uvicorn
    uvicorn.run("run:app", host="127.0.0.1", port=int(os.getenv("PORT", 8000)), reload=False)

def start_all_services():
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()

    time.sleep(3) 

    # 2. Worker
    worker_cmd = "python backend/core/worker.py"
    worker_proc = run_process(worker_cmd)

    time.sleep(1)
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        worker_proc.terminate()
        sys.exit(0)

# ---------------------
# Chạy nếu trực tiếp gọi run.py
# ---------------------
if __name__ == "__main__":
    start_all_services()