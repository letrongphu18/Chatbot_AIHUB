from fastapi import APIRouter, Body, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from backend.auth.api_key_auth import check_api_key
from backend.database.load_pages_config import PageConfig
from backend.database.session import SessionLocal
from backend.schemas.page_config import PageConfigIn
# from backend.database.crud import get_all_configs, get_config_by_id, add_config, update_config, delete_config, get_platform_credential
from backend.database import crud
from backend.schemas.page_schema import PagePayload
router = APIRouter(dependencies=[Depends(check_api_key)])

# Dependency để lấy DB session

# -----------------------------
# Load danh sách tất cả page
# -----------------------------

@router.get("/api/pages")
def get_pages():
    try:
        pages = crud.get_all_configs()
        return {"pages": pages}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving pages: {str(e)}")
    
# -----------------------------
# Lấy chi tiết page theo page_id
# -----------------------------
@router.get("/api/page_details/{channel_id}")
def get_page_details(channel_id: int):
    config = crud.get_page_by_id(channel_id)
    if not config:
        raise HTTPException(status_code=404, detail="Page config not found")
    return config

# -----------------------------
# Thêm thông tin page
# -----------------------------
@router.post("/api/page")
def add_page(payload: dict = Body(...)):
    config = payload.get("config")
    platform = payload.get("platform")
    success = crud.add_page(config, platform)
    if not success:
        raise HTTPException(status_code=400, detail="Page config already exists")
    return {"message": "Page config added"}


# -----------------------------
# Cập nhật thông tin page
# -----------------------------
@router.put("/api/page/{channel_id}")
def update_page_config(channel_id: int, payload: PagePayload = Body(...)):
    platform = payload.platform
    config = payload.config
    print("Updating page:", channel_id, platform, config)
    success = crud.update_page(channel_id, platform, config)
    if not success:
        raise HTTPException(status_code=404, detail="Page config not found")
    return {"message": "Page config updated", "channel_id": channel_id}


# -----------------------------
# Xóa thông tin page
# -----------------------------
@router.delete("/api/page/{channel_id}")
def delete_page(channel_id: int):
    success = crud.delete_page(channel_id)
    if not success:
        raise HTTPException(status_code=404, detail="Page config not found")
    return {"message": "Page config deleted", "channel_id": channel_id}