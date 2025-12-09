from app.core.config import supabase
from app.schemas.check import CheckCreate
from fastapi import HTTPException

def create_check(check: CheckCreate):
    """
    Inserts a new check record into the database after validating the data.
    """
    if not all([check.amount, check.bank_name, check.check_number, check.beneficiary_id]):
        raise HTTPException(status_code=400, detail="All fields except check_image_url are required.")

    try:
        data = supabase.table("checks").insert(check.dict()).execute()
        return data.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def get_check_statistics():
    """
    Retrieves the count of checks for each status.
    """
    try:
        pending_count = supabase.table("checks").select("id", count="exact").eq("status", "pending").execute().count
        approved_count = supabase.table("checks").select("id", count="exact").eq("status", "approved").execute().count
        rejected_count = supabase.table("checks").select("id", count="exact").eq("status", "rejected").execute().count

        return {
            "pending": pending_count,
            "approved": approved_count,
            "rejected": rejected_count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
