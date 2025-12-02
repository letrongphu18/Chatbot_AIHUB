
import re
import json
from backend.core.schemas import LeadData

class FlowEngine:
    def __init__(self, redis_client):
        self.redis = redis_client

    def calculate_score(self, phone, email, stage, classification):
        """
        Hàm chấm điểm Lead (Lead Scoring Algorithm)
        Thang điểm: 0 - 100
        """
        score = 10 
        
    
        if phone or email: 
            score += 50
        
        # này là điểm phân loại khách hàng
        classification = (classification or "").lower()
        if "nghien_nang" in classification: score += 15  
        if "vip" in classification: score += 20          
        if "stress" in classification: score += 10       
    
        stage = (stage or "").upper()
        if stage == "HOT": score += 20
        elif stage == "WARM": score += 10
        elif stage == "QUALIFIED": score += 5
        
      
        return min(score, 100)

    def process_ai_result(self, sender_id, message_text, ai_json, config):
        """
        Điều phối dữ liệu từ AI sang CRM
        """
        reply_text = ai_json.get("reply_text") or ai_json.get("reply_to_user") or "..."
        
     
        analysis = ai_json.get("analysis") or {}
        detected_info = ai_json.get("detected_info") or {}
        tags = ai_json.get("tags") or []
        
  
        classification = ai_json.get("classification") or ""
        need_phone = ai_json.get("need_phone", False)
        next_state = ai_json.get("next_state") or "DEFAULT"
        
      
        sub_topic = analysis.get("sub_topic") or ""
        intent = ai_json.get("intent") or sub_topic or "general_inquiry"

    #    này là tìm số điện thoại
        phone = self.extract_phone_number(message_text)
        email = self.extract_email(message_text)
        
       
        if not phone and detected_info: 
            phone = detected_info.get("phone")
        if not email and detected_info:
            email = detected_info.get("email")

       
        stage = "NEW"
        
    
        if classification and classification.lower() != "unknown":
            stage = "QUALIFIED"
        if "warm" in classification.lower() or "muon_mua" in intent.lower():
            stage = "WARM"
        if phone or email:
            stage = "HOT"

        # này là tính điểm Score sau khi đã có Stage
        lead_score = self.calculate_score(phone, email, stage, classification)

       
        ai_notes = analysis.get('customer_behavior_notes', '')
        full_notes = f"[AI]: {ai_notes} | Stage: {stage} | Class: {classification}"

        lead = LeadData(
            full_name=f"User {sender_id}",
            phone=phone,
            email=email,
            facebook_uid=str(sender_id),
            profile_link=f"https://facebook.com/{sender_id}",
            
            # Phân loại
            topic=config.get("topic_id") or config.get("topic", "general"),
            subtopic=sub_topic,
            tags=tags,
            intent=intent,
            classification=classification,
            
            # Nguồn
            lead_source="facebook_chatbot",
            source_page=config.get("page_name", "Unknown Page"),
            channel="facebook",
            
            # Đánh giá 
            data_raw=message_text,
            score=lead_score,
            
            # Ghi chú & Stage (Nếu schema có field stage thì map vào, ko thì để trong note)
            notes=full_notes
           
        )

       
        action_signal = "REPLY"
        
       
        if phone or email:
            action_signal = "PUSH_CRM"
            print(f"ĐÃ BẮT ĐƯỢC SĐT/EMAIL -> KÍCH HOẠT PUSH CRM NGAY!")
            
       
        elif lead_score >= 80:
            action_signal = "PUSH_CRM"
            print(f" KHÁCH RẤT TIỀM NĂNG (Score {lead_score}) -> Báo CRM để Sale hỗ trợ")
            
        else:
            # Còn lại: Chỉ chat, không làm phiền CRM
            print(f" Đang dẫn dắt... (Chưa có SĐT -> Không đẩy CRM)")

        
        if self.redis:
            
            if next_state and next_state != "DEFAULT":
                self.redis.hset(f"session:{sender_id}", "current_state", next_state)
            
          
            for tag in tags:
                self.redis.rpush(f"tags:{sender_id}", tag)

        return {
            "text_to_send": reply_text,
            "action": action_signal,
            "lead_data": lead.to_dict()
        }



    def extract_phone_number(self, text):
        """Tìm SĐT VN (An toàn tuyệt đối)"""
        if not text: return None
        # Xóa nhiễu
        clean_text = text.replace('.', '').replace('-', '').replace(' ', '')
        # Regex: Đầu 03,05,07,08,09 + 8 số
        matches = re.findall(r'0[3|5|7|8|9]\d{8}', clean_text)
        return matches[0] if matches else None

    def extract_email(self, text):
        """Tìm Email (An toàn tuyệt đối)"""
        if not text: return None
        match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
        return