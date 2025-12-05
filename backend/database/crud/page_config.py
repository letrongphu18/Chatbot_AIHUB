from sqlalchemy.orm import Session
from backend.database.models.page_config import PageConfig

import json

# -----------------------------
# Lấy page config theo page_id
# -----------------------------

def get_config_by_id(db: Session, page_id: str):
    cfg = db.query(PageConfig).filter(PageConfig.fb_pageid == page_id).first()
    return cfg.to_dict() if cfg else None

# -----------------------------
# Thêm page config
# -----------------------------
def add_config(db: Session, config: dict):
    fbid = config["facebook_settings"]["FB_PAGEID"]

    exists = db.query(PageConfig).filter(PageConfig.fb_pageid == fbid).first()
    if exists:
        return False

    new_cfg = PageConfig(
        fb_pageid=fbid,
        topic_id=config["topic_id"],
        config_version=config["config_version"],
        meta_data=json.dumps(config["meta_data"], ensure_ascii=False),
        content_strategy=json.dumps(config["content_strategy"], ensure_ascii=False),
        logic_rules=json.dumps(config["logic_rules"], ensure_ascii=False),
        system_settings=json.dumps(config["system_settings"], ensure_ascii=False),
        facebook_settings=json.dumps(config["facebook_settings"], ensure_ascii=False),
    )

    db.add(new_cfg)
    db.commit()
    db.refresh(new_cfg)
    return True


# -----------------------------
# Cập nhật page config theo page_id
# -----------------------------
def update_page_config(db: Session, page_id: str, config: dict):
    cfg = db.query(PageConfig).filter(PageConfig.fb_pageid == page_id).first()
    if not cfg:
        return False

    cfg.topic_id = config["topic_id"]
    cfg.config_version = config["config_version"]
    cfg.meta_data = json.dumps(config["meta_data"], ensure_ascii=False)
    cfg.content_strategy = json.dumps(config["content_strategy"], ensure_ascii=False)
    cfg.logic_rules = json.dumps(config["logic_rules"], ensure_ascii=False)
    cfg.system_settings = json.dumps(config["system_settings"], ensure_ascii=False)
    cfg.facebook_settings = json.dumps(config["facebook_settings"], ensure_ascii=False)

    db.commit()
    return True


# -----------------------------
# Xóa page config theo page_id
# -----------------------------
def delete_page_config(db: Session, page_id: str):
    cfg = db.query(PageConfig).filter(PageConfig.fb_pageid == page_id).first()
    if not cfg:
        return False
    db.delete(cfg)
    db.commit()
    return True

# -----------------------------
# Lấy tất cả page configs
# -----------------------------
def get_all_configs(db: Session):
    return [cfg.to_dict() for cfg in db.query(PageConfig).all()]

# -----------------------------
# Load tất cả FB tokens từ DB
def load_all_fb_tokens(db: Session) -> dict:
    tokens = {}

    for row in db.query(PageConfig).all():
        fb = json.loads(row.facebook_settings)
        pid = fb.get("FB_PAGEID")
        token = fb.get("FB_PAGE_ACCESS_TOKEN")
        if pid and token:
            tokens[pid] = token
    
    return tokens
