from fastapi import APIRouter, Depends, HTTPException
from backend.auth.api_key_auth import check_api_key
from backend.database import crud

router = APIRouter(dependencies=[Depends(check_api_key)])

@router.get("/api/statistics")
def get_statistics():
    try:
        statis = crud.get_statistics()
        return statis
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving statistics: {str(e)}")