from pydantic import BaseModel
from typing import List, Dict

class MetaData(BaseModel):
    brand_default: str
    description: str
    tone_style: str
    main_objective: str

class ContentStrategy(BaseModel):
    core_questions: List[str]
    phone_request_template: str
    closing_strategy: str

class LogicRules(BaseModel):
    classification_rules: Dict[str, str]

class SystemSettings(BaseModel):
    call_me: str
    call_user: str

class FacebookSettings(BaseModel):
    FB_PAGE_ACCESS_TOKEN: str
    FB_VERIFY_TOKEN: str
    FB_PAGEID: str

class PageConfigIn(BaseModel):
    topic_id: str
    config_version: str
    meta_data: MetaData
    content_strategy: ContentStrategy
    logic_rules: LogicRules
    system_settings: SystemSettings
    facebook_settings: FacebookSettings
