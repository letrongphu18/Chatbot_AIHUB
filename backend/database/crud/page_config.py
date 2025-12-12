from datetime import datetime
from logging import config
from sqlalchemy.orm import Session
from backend.database.models.page_config import Channel, PageConfig
from sqlalchemy import cast, String
import json

from backend.database.session import SessionLocal

# -----------------------------
# Lấy page config theo page_id
# -----------------------------
def get_db_instance():
    db = SessionLocal()
    try:
        return db
    finally:
        pass 
db = get_db_instance()

# -----------------------------
# Dùng cho train chatbot
def get_config_by_page_id(page_id: int):
    channel = db.query(Channel).filter(Channel.page_id == page_id).first()
    if not channel:
        return None
    cfg = db.query(PageConfig).filter(PageConfig.channel_id == channel.id).first()
    if not cfg or not cfg.config_json:
        return None

    # Chuyển cfg.config_json sang dict nếu cần
    if isinstance(cfg.config_json, str):
        try:
            config = json.loads(cfg.config_json)
        except json.JSONDecodeError:
            # Nếu JSON không hợp lệ, trả về None
            return None
    elif isinstance(cfg.config_json, dict):
        config = dict(cfg.config_json)  # copy dict
    else:
        return None
    config["topic_id"] = cfg.topic_id
    config["config_version"] = cfg.config_version
    config["page_id"] = channel.page_id
    return config if config else None

def get_config_by_channel(channel_id: int):
    cfg = db.query(PageConfig).filter(PageConfig.channel_id == channel_id).first()
    return cfg.to_dict() if cfg else None

def get_channel(channel_id: int): #Tạm thời chưa dùng platform
    cred = (
        db.query(Channel)
        .filter(
            Channel.id == channel_id
        )
        .first()
    )
    return cred.to_dict() if cred else None

def add_page(config: dict, platform:dict):
    page_id = platform.get("page_id")
    access_token = platform.get("access_token")

    if not page_id or not access_token :
        raise ValueError("platform info incomplete")

    exists = db.query(Channel).filter(
        Channel.page_id == page_id
    ).first()

    if exists:
        return False
    
    cred  = Channel(
        page_id=page_id,
        platform=platform.get("platform") ,
        access_token=access_token,
        verify_token=platform.get("verify_token"),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(cred)
    db.flush()
    if not config:
        config = {
            "topic_id": "",
            "config_version": "1.0",
            "config_json": {}
        }
    
    new_cfg = PageConfig(
        channel_id=cred.id,
        topic_id=config["topic_id"],
        config_version=config["config_version"],
        config_json=config.get("config_json", {}),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(new_cfg)

    
    db.commit()
    return True


def update_page(channel_id: int, platform: dict , config: dict ):
    cfg = (
        db.query(PageConfig)
        .filter(PageConfig.channel_id == channel_id)
        .first()
    )
    if not cfg:
        return False

    cred = (
        db.query(Channel)
        .filter(
            Channel.id == channel_id,
        )
        .first()
    )
    if not cred:
        return False

    # ---- UPDATE CONFIG_JSON ----
    if config:
        cfg.topic_id = config.get("topic_id", cfg.topic_id)
        cfg.config_version = config.get("config_version", cfg.config_version)
        raw = config.get("config_json")

        if isinstance(raw, str):
            raw = raw.strip()
            if raw == "" or raw.lower() == "none":
                raw = {}
            else:
                try:
                    raw = json.loads(raw)
                except:
                    raise ValueError("config_json is not valid JSON")
        cfg.config_json = raw
        cfg.updated_at = datetime.utcnow()

    # ---- UPDATE PLATFORM TOKEN ----
    if platform:
        if platform.get("page_id"):
            cred.page_id = platform["page_id"]
        if platform.get("access_token"):
            cred.access_token = platform["access_token"]
        if platform.get("verify_token"):
            cred.verify_token = platform["verify_token"]
        if platform.get("refresh_token"):
            cred.refresh_token = platform["refresh_token"]
        if platform.get("secret_key"):
            cred.secret_key = platform["secret_key"]

        cred.updated_at = datetime.utcnow()

    db.commit()
    return True


def delete_page(channel_id: int) -> bool:
    cfg = (
        db.query(PageConfig)
        .filter(
            PageConfig.channel_id == channel_id,
        )
        .first()
    )

    if cfg:
        db.delete(cfg)

    cred = (
        db.query(Channel)
        .filter(
            Channel.id == channel_id,
        )
        .first()
    )

    if cred:
        db.delete(cred)

    if not cred and not cfg:
        return False

    db.commit()
    return True

# dùng trong api quản trị danh sách page
def get_all_configs():
    try:
        records = db.query(
            PageConfig.channel_id,
            cast(PageConfig.config_json["meta_data"]["brand_default"], String).label("brand_default")
        ).all()

        # Dùng list comprehension để parse JSON một lần
        result = [
            {
                "id": r.channel_id,
                "name": json.loads(r.brand_default) if r.brand_default else None
            }
            for r in records
        ]
        return result
    except Exception as e:
        raise Exception(f"Database error in get_all_configs: {str(e)}")

# dùng trong worker để load tất cả token fb
def load_all_fb_tokens() -> dict:
    return {
        plf.page_id: plf.access_token
        for plf in db.query(Channel).all()
    }
    
