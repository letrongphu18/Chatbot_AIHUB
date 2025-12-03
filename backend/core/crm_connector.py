# app/crm_connector.py
import requests
import json
import os
import redis
from backend.core.redis_client import r

# Cấu hình Charm.Contact (Sau này thay bằng URL thật giờ tui làm mock thôi)
CHARM_API_URL = os.getenv("CHARM_API_URL", "http://127.0.0.1:8000/mock-crm/leads")
CHARM_API_KEY = os.getenv("CHARM_API_KEY", "mock-key")

class CRMConnector:
    # def __init__(self):
    #     redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    #     self.redis = redis.from_url(redis_url)

    def push_lead(self, lead_data: dict):
        """
        Quy trình chuẩn:
        1. Check xem khách có chưa (Deduplication).
        2. Nếu chưa -> Tạo mới (Create).
        3. Nếu có rồi -> Cập nhật (Update).
        4. Nếu lỗi -> Đẩy vào Queue Retry.
        """
        print(f" Đang bắn Lead sang CRM: {lead_data['phone']}...")

        try:
            
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {CHARM_API_KEY}"
            }
            
            response = requests.post(
                CHARM_API_URL, 
                json=lead_data,
                headers=headers,
                timeout=10 
            )
            
        
            if response.status_code in [200, 201]:
                print(f"✅ CRM Success: Deal ID {response.json().get('deal_id', 'Unknown')}")
                return True
                
            else:
                print(f" CRM Trả lỗi {response.status_code}: {response.text}")
             
                raise Exception(f"CRM Error {response.status_code}")

        except Exception as e:
       
            print(f" LỖI KẾT NỐI CRM: {e}")
            print(" Đang đẩy vào hàng đợi Retry (crm_retry_queue)...")
            
          
            self.retry_push(lead_data)
            return False

    def retry_push(self, lead_data):
        """Đẩy lead bị lỗi vào Redis để thử lại sau"""
        try:
            self.redis.rpush("crm_retry_queue", json.dumps(lead_data))
        except Exception as e:
            print(f" LỖI NGHIÊM TRỌNG: Không thể lưu Retry! {e}")