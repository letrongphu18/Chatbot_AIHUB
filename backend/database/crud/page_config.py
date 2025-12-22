from datetime import datetime
from logging import config
import requests
from sqlalchemy.orm import Session
from backend.database.models.page_config import Channel, PageConfig
from sqlalchemy import cast, String, desc
import json

from backend.database.session import SessionLocal

# -----------------------------
# Lấy page config theo page_id
# -----------------------------
# def get_db_instance():
#     db = SessionLocal()
#     try:
#         return db
#     except:
#         db.rollback() 
#         raise
#     finally:
#         pass 
# db = get_db_instance()

# -----------------------------
# Dùng cho train chatbot
def get_config_by_page_id(db: Session, page_id: int):
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


def get_config_by_channel(db: Session, channel_id: int):
    cfg = db.query(PageConfig).filter(PageConfig.channel_id == channel_id).first()
    return cfg.to_dict() if cfg else None

def get_channel(db: Session, channel_id: int): #Tạm thời chưa dùng platform
    cred = (
        db.query(Channel)
        .filter(
            Channel.id == channel_id
        )
        .first()
    )
    return cred.to_dict() if cred else None

# Dùng trong page api để lấy chi tiết page
def get_page_by_id(db: Session, channel_id: int):
    channel = db.query(Channel).filter(Channel.id == channel_id).first()
    if not channel:
        return None

    config = db.query(PageConfig).filter(PageConfig.channel_id == channel.id).first()

    # Nếu không có config thì trả mặc định
    config_json = config.config_json if config and config.config_json else "{}"
    meta_data = config_json.get("meta_data", {})
    content = config_json.get("content_strategy", {})
    system = config_json.get("system_settings", {})

    data = {
        "id": channel.id,
        "page_id": channel.page_id,
        "access_token": channel.access_token,

        "config_version": getattr(config, "config_version", None),

        # meta_data
        "brand_default": meta_data.get("brand_default", ""),
        "description": meta_data.get("description", ""),
        "tone_style": meta_data.get("tone_style", ""),
        "main_objective": meta_data.get("main_objective", ""),

        # content_strategy
        "core_questions": content.get("core_questions", []),
        "phone_request_template": content.get("phone_request_template", []),
        "closing_strategy": content.get("closing_strategy", ""),
        "classification_rules": content.get("classification_rules", {}),

        # system_settings
        "call_me": system.get("call_me", ""),
        "call_user": system.get("call_user", ""),
    }

    return data

# Dùng trong page api để thêm page mới
def add_page(db: Session, page: dict):
    page_id = page.get("page_id")
    access_token = page.get("access_token")
    if not page_id or not access_token :
        raise ValueError("platform info incomplete")

    exists = db.query(Channel).filter(
        Channel.page_id == page_id
    ).first()

    if exists:
        return False
    
    cred  = Channel(
        page_id=page_id,
        platform="facebook", 
        access_token=access_token,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(cred)
    db.flush()
    topic_id = page.get("topic_id", "")
    config_version = page.get("config_version", "")
    brand_default = page.get("brand_default", "")
    description = page.get("description", "")
    tone_style = page.get("tone_style", "")
    main_objective = page.get("main_objective", "")
    core_questions = page.get("core_questions", [])
    phone_request_template = page.get("phone_request_template", [])
    closing_strategy = page.get("closing_strategy", "")
    classification_rules = page.get("classification_rules", {})
    call_me = page.get("call_me", "")
    call_user = page.get("call_user", "")
    config_json = {
        "meta_data": {
            "brand_default": brand_default,
            "description": description,
            "tone_style": tone_style,
            "main_objective": main_objective,
        },
        "content_strategy": {
            "core_questions": core_questions,
            "phone_request_template": phone_request_template,
            "closing_strategy": closing_strategy,
            "classification_rules": classification_rules,
        },
        "system_settings": {
            "call_me": call_me,
            "call_user": call_user,
        }
    }

    new_cfg = PageConfig(
        channel_id=cred.id,
        topic_id=topic_id,
        config_version=config_version,
        config_json=config_json,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(new_cfg)
    db.commit()
    return True


# def add_page(config: dict, platform:dict):
#     page_id = platform.get("page_id")
#     access_token = platform.get("access_token")

#     if not page_id or not access_token :
#         raise ValueError("platform info incomplete")

#     exists = db.query(Channel).filter(
#         Channel.page_id == page_id
#     ).first()

#     if exists:
#         return False
    
#     cred  = Channel(
#         page_id=page_id,
#         platform=platform.get("platform") ,
#         access_token=access_token,
#         verify_token=platform.get("verify_token"),
#         created_at=datetime.utcnow(),
#         updated_at=datetime.utcnow()
#     )
#     db.add(cred)
#     db.flush()
#     if not config:
#         config = {
#             "topic_id": "",
#             "config_version": "1.0",
#             "config_json": {}
#         }
    
#     new_cfg = PageConfig(
#         channel_id=cred.id,
#         topic_id=config["topic_id"],
#         config_version=config["config_version"],
#         config_json=config.get("config_json", {}),
#         created_at=datetime.utcnow(),
#         updated_at=datetime.utcnow(),
#     )
#     db.add(new_cfg)

    
#     db.commit()
#     return True


def update_page(db: Session, channel_id: int, page: dict):
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
    
    if page:
        # ---- UPDATE PLATFORM TOKEN ----
        if page.get("page_id"):
            cred.page_id = page.get("page_id")
        if page.get("access_token"):
            cred.access_token = page.get("access_token")
        cred.verify_token = page.get("verify_token", cred.verify_token)
        cred.refresh_token = page.get("refresh_token", cred.refresh_token)
        cred.secret_key = page.get("secret_key", cred.secret_key)
        cred.updated_at = datetime.utcnow()

        # ---- UPDATE PAGE CONFIG ----
        cfg.topic_id = page.get("topic_id", cfg.topic_id)
        cfg.config_version = page.get("config_version", cfg.config_version)
        brand_default = page.get("brand_default", "")
        description = page.get("description", "")
        tone_style = page.get("tone_style", "")
        main_objective = page.get("main_objective", "")
        core_questions = page.get("core_questions", [])
        phone_request_template = page.get("phone_request_template", [])
        closing_strategy = page.get("closing_strategy", "")
        classification_rules = page.get("classification_rules", {})
        call_me = page.get("call_me", "")
        call_user = page.get("call_user", "")
        config_json = {
                        "meta_data": {
                            "brand_default": brand_default,
                            "description": description,
                            "tone_style": tone_style,
                            "main_objective": main_objective,
                        },
                        "content_strategy": {
                            "core_questions": core_questions,
                            "phone_request_template": phone_request_template,
                            "closing_strategy": closing_strategy,
                            "classification_rules": classification_rules,
                        },
                        "system_settings": {
                            "call_me": call_me,
                            "call_user": call_user,
                        }
                    }
        cfg.config_json = config_json
        cfg.updated_at = datetime.utcnow()
    db.commit()
    return True


def delete_page(db: Session, channel_id: int) -> bool:
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
def get_all_configs(db: Session):
    try:
        
        records = db.query(
            PageConfig.channel_id,
            cast(PageConfig.config_json["meta_data"]["brand_default"], String).label("brand_default")
        ).order_by(desc(PageConfig.created_at)).all()

        # Dùng list comprehension để parse JSON một lần
        result = [
            {
                "id": r.channel_id,
                "page_id": db.query(Channel.page_id).filter(Channel.id == r.channel_id).scalar(),
                "name": json.loads(r.brand_default) if r.brand_default else None
            }
            for r in records
        ]
        return result
    except Exception as e:
        raise Exception(f"Database error in get_all_configs: {str(e)}")

# dùng trong conversation_routes để hiển thị tên page
def get_page_name_by_id(page_id: int, access_token: str) -> str:
    page_url = f"https://graph.facebook.com/v17.0/{page_id}"
    page_params = {
        "fields": "name",
        "access_token": access_token
    }
    page_response = requests.get(page_url, params=page_params)
    try:
        page_data = page_response.json()
    except ValueError:
        raise Exception("Không thể parse JSON từ response Facebook")
    if "error" in page_data:
        raise Exception(f"Facebook API error: {page_data['error']}")
    page_name = page_data.get("name")
    if not page_name:
        raise Exception("Không tìm thấy tên page")
    return page_name

# dùng trong conversation_routes để lấy token theo page_id
def get_token_by_page_id(db: Session,page_id: int) -> str:
    channel = db.query(Channel).filter(Channel.page_id == page_id).first()
    if not channel:
        return None
    return channel.access_token

# dùng trong worker để load tất cả token fb
def load_all_fb_tokens(db: Session) -> dict:
    return {
        plf.page_id: plf.access_token
        for plf in db.query(Channel).all()
    }
    
