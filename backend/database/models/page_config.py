
#SQLAlchemy models
from sqlalchemy import JSON, Column, DateTime, ForeignKey, Integer, String, Text
from backend.database.session import Base
from sqlalchemy.orm import relationship
import json

class PageConfig(Base):
    __tablename__ = "page_configs"
    id = Column(Integer, primary_key=True, autoincrement=True)
    channel_id = Column(Integer, ForeignKey("channels.id"), nullable=False)
    channel = relationship("Channel", back_populates="page_configs")
    topic_id = Column(String(255), nullable=False)
    config_version = Column(String(50), nullable=False)
    config_json = Column(JSON, nullable=False)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    def to_dict(self):
        return {
            "id": self.id,
            "channel_id": self.channel_id,
            "topic_id": self.topic_id,
            "config_version": self.config_version,
            "config_json": self.config_json,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

class Channel(Base):
    __tablename__ = "channels"

    id = Column(Integer, primary_key=True, autoincrement=True)
    page_id = Column(String(255), nullable=False, index=True) # id fanpage
    platform = Column(String(50), nullable=False)  # facebook / zalo / telegram
    
    access_token = Column(String(500), nullable=False)  
    refresh_token = Column(String(500), nullable=True)
    verify_token = Column(String(255), nullable=True)
    secret_key = Column(String(255), nullable=True)

    expires_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    page_configs = relationship("PageConfig", back_populates="channel")
    def to_dict(self):
        return {
            "id": self.id,
            "page_id": self.page_id,
            "platform": self.platform,
            "access_token": self.access_token,
            "refresh_token": self.refresh_token,
            "verify_token": self.verify_token,
            "secret_key": self.secret_key,
            "expires_at": self.expires_at,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
