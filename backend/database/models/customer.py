
#SQLAlchemy models
from sqlalchemy import JSON, Column, DateTime, ForeignKey, Integer, String, Text
from backend.database.session import Base
from sqlalchemy.orm import relationship
import json

class Customer(Base):
    __tablename__ = "customers"
    id = Column(Integer, primary_key=True, autoincrement=True)
    full_name = Column(String(255), nullable=False)
    phone = Column(String(50), nullable=False)
    email = Column(String(255), nullable=False)
    conversation_id = Column(String(255), nullable=False)
    page_id = Column(String(255), nullable=False)
    tags = Column(String(255), nullable=False)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    def to_dict(self):
        return {
            "id": self.id,
            "full_name": self.full_name,
            "phone": self.phone,
            "email": self.email,
            "conversation_id": self.conversation_id,
            "page_id": self.page_id,
            "tags": self.tags,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
