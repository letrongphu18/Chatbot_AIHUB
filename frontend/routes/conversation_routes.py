import json
from typing import Any
from fastapi.responses import RedirectResponse
import httpx

from fastapi import APIRouter, Body, Form, Request
from fastapi.templating import Jinja2Templates


router = APIRouter()
templates = Jinja2Templates(directory="frontend/templates")

@router.get("/conversations")
def get_pages(request: Request):
    print("Fetching page configurations...")
    api_url = "http://localhost:8099/api/conversations"
    headers = {"X-API-KEY": "abc123"}
    
    response = httpx.get(api_url, headers=headers)
    conversations = response.json().get("conversations", [])
    print(f"Retrieved {len(conversations)} conversations.")

    return templates.TemplateResponse(
        "conversations.html",
        {"request": request, "conversations": conversations}
    )

