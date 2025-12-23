
#SQLAlchemy models
from typing import List
from sqlalchemy import JSON, Column, DateTime, ForeignKey, Integer, String, Text
from backend.database.session import Base
from sqlalchemy.orm import relationship
import json

class LeadData(Base):
    __tablename__ = "lead_data"

    id = Column(Integer, primary_key=True, autoincrement=True)
    # 1. Thông tin cơ bản
    full_name = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    email = Column(String(255), nullable=True)

    facebook_uid = Column(String(255), nullable=True)
    profile_link = Column(String(255), nullable=True)
    
    # 2. Phân loại
    topic = Column(String(255), nullable=True)             
    subtopic = Column(String(255), nullable=True)             

    tags = Column(JSON, nullable=True)
    intent = Column(String(255), nullable=True)
    classification = Column(String(255), nullable=True)
    stage = Column(String(50), nullable=True)
    # 3. Nguồn & Kênh
    lead_source = Column(String(255), nullable=True)
    source_page = Column(String(255), nullable=True)
    channel = Column(String(255), nullable=True)
    
    page_id = Column(String(255), nullable=True)
    conversation_id = Column(String(255), nullable=True)
    # 4. Dữ liệu thô & Đánh giá
    data_raw = Column(Text, nullable=True)
    score = Column(Integer, nullable=True)
    # Phụ trợ
    notes = Column(Text, nullable=True)

    def to_dict(self):
        return self.__dict__

