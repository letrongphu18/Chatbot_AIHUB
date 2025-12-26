# app/fb_helper.py
import os
import requests
import json

class FacebookClient:
    #def __init__(self):
    def __init__(self, page_tokens: dict = None):
        # Lấy Token từ file .env
        if page_tokens:
            self.page_tokens  = page_tokens
        else:
            self.page_tokens = {}
        self.api_url = "https://graph.facebook.com/v18.0/me/messages"

    def send_text_message(self, recipient_id, text, page_id=None):
        """
        Gửi tin nhắn văn bản trả lời khách hàng
        """
        if not self.page_tokens:
            print(" Không có token Facebook nào, kiểm tra JSON config")
            return
         # lấy token tương ứng
        if page_id:
            token = self.page_tokens.get(page_id)
            if not token:
                print(f" Không tìm thấy token cho page_id={page_id}")
                return
        else:
            token = next(iter(self.page_tokens.values()))  # token đầu tiên

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token }"
        }
        
        payload = {
            "recipient": {"id": recipient_id},
            "message": {"text": text},
            "messaging_type": "RESPONSE"
        }

        try:
            response = requests.post(self.api_url, headers=headers, json=payload)
            response.raise_for_status() # này sẽ trả lại lỗi nếu FB từ chối nha
            print(f" Đã gửi tin nhắn cho khách {recipient_id}: {text[:20]}...")
        except Exception as e:
            print(f" Lỗi gửi tin FB: {e}")
            if response:
                print(f" Chi tiết FB báo: {response.text}")