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
    if db.query(PageConfig).filter(PageConfig.fb_pageid == config["facebook_settings"]["FB_PAGEID"]).first():
        return False
    cfg = PageConfig(
        fb_pageid=config["facebook_settings"]["FB_PAGEID"],
        topic_id=config["topic_id"],
        config_version=config["config_version"],
        meta_data=json.dumps(config["meta_data"]),
        content_strategy=json.dumps(config["content_strategy"]),
        logic_rules=json.dumps(config["logic_rules"]),
        system_settings=json.dumps(config["system_settings"]),
        facebook_settings=json.dumps(config["facebook_settings"])
    )
    db.add(cfg)
    db.commit()
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
    cfg.meta_data = json.dumps(config["meta_data"])
    cfg.content_strategy = json.dumps(config["content_strategy"])
    cfg.logic_rules = json.dumps(config["logic_rules"])
    cfg.system_settings = json.dumps(config["system_settings"])
    cfg.facebook_settings = json.dumps(config["facebook_settings"])
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
    # Lấy toàn bộ config từ DB
    rows = db.query(PageConfig).all()

    for row in rows:
        try:
            fb_settings = json.loads(row.facebook_settings)
            page_id = fb_settings.get("FB_PAGEID")
            token   = fb_settings.get("FB_PAGE_ACCESS_TOKEN")
            if page_id and token:
                tokens[page_id] = token
        except:
            continue
    return tokens