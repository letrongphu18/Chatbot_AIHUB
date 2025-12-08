from pydantic import BaseModel
from typing import Dict, Any

class PagePayload(BaseModel):
    platform: Dict[str, Any]
    config: Dict[str, Any]
