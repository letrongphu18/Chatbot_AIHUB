from fastapi import APIRouter, Depends, HTTPException
from backend.auth.api_key_auth import check_api_key
from backend.database import crud

router = APIRouter(dependencies=[Depends(check_api_key)])

@router.get("/api/leads")
def get_leads():
    try:
        leads = crud.get_all_leads()
        return {"leads": leads}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving leads: {str(e)}")