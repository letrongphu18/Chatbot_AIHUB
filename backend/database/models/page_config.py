
from sqlalchemy import Column, Integer, String, Text
from backend.database.session import Base
import json
class PageConfig(Base):
    __tablename__ = "page_configs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    fb_pageid = Column(String(255), unique=True, index=True, nullable=False)

    topic_id = Column(String(255))
    config_version = Column(String(50))

    meta_data = Column(Text)
    content_strategy = Column(Text)
    logic_rules = Column(Text)
    system_settings = Column(Text)
    facebook_settings = Column(Text)

    def to_dict(self):
        return {
            "fb_pageid": self.fb_pageid,
            "topic_id": self.topic_id,
            "config_version": self.config_version,
            "meta_data": json.loads(self.meta_data),
            "content_strategy": json.loads(self.content_strategy),
            "logic_rules": json.loads(self.logic_rules),
            "system_settings": json.loads(self.system_settings),
            "facebook_settings": json.loads(self.facebook_settings),
        }


# from sqlalchemy import Column, String, Text
# from backend.database.session import Base
# import json

# class PageConfig(Base):
#     __tablename__ = "page_configs"

#     fb_pageid = Column(String, primary_key=True, index=True)
#     topic_id = Column(String, nullable=False)
#     config_version = Column(String, nullable=False)
#     meta_data = Column(Text, nullable=False)
#     content_strategy = Column(Text, nullable=False)
#     logic_rules = Column(Text, nullable=False)
#     system_settings = Column(Text, nullable=False)
#     facebook_settings = Column(Text, nullable=False)

#     def to_dict(self):
#         return {
#             "topic_id": self.topic_id,
#             "config_version": self.config_version,
#             "meta_data": json.loads(self.meta_data),
#             "content_strategy": json.loads(self.content_strategy),
#             "logic_rules": json.loads(self.logic_rules),
#             "system_settings": json.loads(self.system_settings),
#             "facebook_settings": json.loads(self.facebook_settings),
#         }
