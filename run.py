import os
import sys
import threading
import time
import subprocess
import socket
from dotenv import load_dotenv
load_dotenv()
from backend.app import create_app

app = create_app()
PORT = int(os.getenv("PORT", 8099))

# ---------------------
# Kiểm tra port
# ---------------------
def is_port_in_use(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex((host, port)) == 0

# ---------------------
# Chạy server
# ---------------------
def run_server():
    import uvicorn
    uvicorn.run("run:app", host="127.0.0.1", port=PORT, reload=False)

# ---------------------
# Chạy worker với retry database
# ---------------------
def run_worker_with_retry():
    max_retry = 5
    delay = 3  # giây
    for attempt in range(1, max_retry + 1):
        try:
            print(f"🔄 Khởi động worker (attempt {attempt})...")
            worker_cmd = "python backend/core/worker.py"
            proc = subprocess.Popen(worker_cmd, shell=True)
            return proc
        except Exception as e:
            print(f"❌ Worker failed: {e}")
            if attempt < max_retry:
                print(f"⏳ Retry sau {delay}s...")
                time.sleep(delay)
            else:
                print("❌ Không thể khởi động worker sau nhiều lần thử. Thoát.")
                sys.exit(1)

# ---------------------
# Main
# ---------------------
def start_all_services():
    # Kiểm tra port trước
    if is_port_in_use("127.0.0.1", PORT):
        print(f"❌ Port {PORT} đang bị chiếm, vui lòng kill tiến trình cũ.")
        sys.exit(1)

    # Start server (thread bình thường)
    server_thread = threading.Thread(target=run_server)
    server_thread.start()

    # Đợi server khởi động
    time.sleep(3)

    # Start worker
    worker_proc = run_worker_with_retry()
    print("✅ Server và Worker đã chạy.")

    try:
        while True:
            # Nếu worker chết, tự restart
            if worker_proc.poll() is not None:
                print("⚠️ Worker bị dừng, restart lại...")
                worker_proc = run_worker_with_retry()
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n⏹ Dừng server và worker...")
        worker_proc.terminate()
        server_thread.join(timeout=1)
        sys.exit(0)

# ---------------------
# Chạy trực tiếp
# ---------------------
if __name__ == "__main__":
    start_all_services()
