from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from backend.auth.api_key_auth import check_api_key
from backend.database.session import SessionLocal
from backend.database.schemas.page_config import PageConfigIn
from backend.database.crud import get_all_configs, get_config_by_id, add_config, update_page_config, delete_page_config
from backend.database import crud
router = APIRouter()

# Dependency để lấy DB session
def get_db_instance():
    db = SessionLocal()
    try:
        return db
    finally:
        pass  

# -----------------------------
# Load danh sách tất cả page
# -----------------------------
@router.get("/api/page_configs", dependencies=[Depends(check_api_key)])
def get_page_configs():
    db = get_db_instance()
    page_configs = crud.get_all_configs(db)
    return {"page_configs": page_configs}


# -----------------------------
# Lấy chi tiết page theo page_id
# -----------------------------
@router.get("/api/page_config_details/{page_id}")
def get_page_config_details(page_id: str):
    db = get_db_instance()
    config = crud.get_config_by_id(db, page_id)
    if not config:
        raise HTTPException(status_code=404, detail="Page config not found")
    return config


# -----------------------------
# Thêm thông tin page
# -----------------------------
@router.post("/api/page_config")
def add_page_config(config: PageConfigIn):
    db = get_db_instance()
    success = crud.add_config(db, config.dict())
    if not success:
        raise HTTPException(status_code=400, detail="Page config already exists")
    return {"message": "Page config added", "page_id": config.facebook_settings.FB_PAGEID}


# -----------------------------
# Cập nhật thông tin page
# -----------------------------
@router.put("/api/page_config/{page_id}")
def update_page_config(page_id: str, config: PageConfigIn):
    db = get_db_instance()
    success = crud.update_page_config(db, page_id, config.dict())
    if not success:
        raise HTTPException(status_code=404, detail="Page config not found")
    return {"message": "Page config updated", "page_id": page_id}


# -----------------------------
# Xóa thông tin page
# -----------------------------
@router.delete("/api/page_config/{page_id}")
def delete_page_config(page_id: str):
    db = get_db_instance()
    success = crud.delete_page_config(db, page_id)
    if not success:
        raise HTTPException(status_code=404, detail="Page config not found")
    return {"message": "Page config deleted", "page_id": page_id}
