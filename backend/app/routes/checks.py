from fastapi import APIRouter
from app.schemas.check import Check, CheckCreate
from app.services.check_service import create_check, get_check_statistics

router = APIRouter()

@router.post("/checks", response_model=Check)
def upload_check_endpoint(check: CheckCreate):
    return create_check(check)

@router.get("/stats")
def get_stats_endpoint():
    return get_check_statistics()
