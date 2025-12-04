import os
from dotenv import load_dotenv
from fastapi import Header, HTTPException
load_dotenv()

VALID_KEYS = os.getenv("VALID_KEYS", "").split(",")

def check_api_key(x_api_key: str = Header(None)):
    if x_api_key not in VALID_KEYS:
        raise HTTPException(
            status_code=403,
            detail="Invalid API KEY"
        )
