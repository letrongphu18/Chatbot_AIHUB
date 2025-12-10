import json
from typing import Any
from fastapi.responses import RedirectResponse
import httpx

from fastapi import APIRouter, Body, Form, Request
from fastapi.templating import Jinja2Templates

from backend.database.crud.page_config import add_page
from backend.database.models.page_config import Channel, PageConfig

router = APIRouter()
templates = Jinja2Templates(directory="frontend/templates")


@router.get("/pages")
def get_pages(request: Request):
    print("Fetching page configurations...")
    api_url = "http://localhost:8099/api/pages"
    headers = {"X-API-KEY": "abc123"}
    
    response = httpx.get(api_url, headers=headers)
    pages = response.json().get("pages", [])
    print(f"Retrieved {len(pages)} page configurations.")

    return templates.TemplateResponse(
        "pages.html",
        {"request": request, "pages": pages}
    )


@router.get("/page_add")
def page_add(request: Request):
    page_config = PageConfig()
    platform_credential = Channel()

    return templates.TemplateResponse(
        "page_add.html",
        {
            "request": request,
            "page_config": page_config,
            "platform_credential": platform_credential
        }
    )


@router.post("/pages/create")
async def page_create(
    topic_id: str = Form(""),
    config_version: str = Form(""),
    platform: str = Form(...),
    page_id: str = Form(...),
    refresh_token: str = Form(""),
    access_token: str = Form(...),
    verify_token: str = Form(""),
    secret_key: str = Form(""),
    config_json: str = Form(...)
):

    payload = {
        "platform": {
            "platform": platform,
            "page_id": page_id,
            "refresh_token": refresh_token,
            "access_token": access_token,
            "verify_token": verify_token,
            "secret_key": secret_key
        },
        "config": {
            "topic_id": topic_id,
            "config_version": config_version,
            "config_json": config_json
        }
    }

    api_url = "http://localhost:8099/api/page"
    headers = {"X-API-KEY": "abc123"}

    async with httpx.AsyncClient() as client:
        response = await client.post(api_url, headers=headers, json=payload)
        try:
            _ = response.json()
            return RedirectResponse(url="/pages", status_code=303)
        except ValueError:
            return {"status": "error", "detail": response.text}


@router.get("/page_edit/{channel_id}")
def page_edit(request: Request, channel_id: str):
    api_url = f"http://localhost:8099/api/page_details/{channel_id}"
    headers = {"X-API-KEY": "abc123"}

    response = httpx.get(api_url, headers=headers)
    if response.status_code != 200:
        return templates.TemplateResponse(
            "page_edit.html",
            {"request": request, "message": "Page configuration not found."},
            status_code=404
        )

    data = response.json()
    pretty_json = json.dumps(data["config"]["config_json"], ensure_ascii=False, indent=2)

    return templates.TemplateResponse(
        "page_edit.html",
        {
            "request": request,
            "page_config": {**data["config"], "config_json_pretty": pretty_json},
            "platform_credential": data["credential"]
        }
    )


@router.post("/pages/update/{channel_id}")
async def submit_update_page(
    channel_id: int,
    topic_id: str = Form(""),
    config_version: str = Form(""),
    page_id: str = Form(...),
    platform: str = Form(...),
    refresh_token: str = Form(""),
    access_token: str = Form(...),
    verify_token: str = Form(""),
    secret_key: str = Form(""),
    config_json: str = Form(...)
):

    payload = {
        "platform": {
            "platform": platform,
            "page_id": page_id,
            "refresh_token": refresh_token,
            "access_token": access_token,
            "verify_token": verify_token,
            "secret_key": secret_key
        },
        "config": {
            "topic_id": topic_id,
            "config_version": config_version,
            "config_json": config_json
        }
    }

    api_url = f"http://localhost:8099/api/page/{channel_id}"
    headers = {"X-API-KEY": "abc123"}

    async with httpx.AsyncClient() as client:
        response = await client.put(api_url, headers=headers, json=payload)
        try:
            _ = response.json()
            return RedirectResponse(url="/pages", status_code=303)
        except ValueError:
            return {"status": "error", "detail": response.text}
