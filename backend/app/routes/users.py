# backend/app/routers/users.py
from fastapi import APIRouter, Depends
from ..utils.auth import get_current_user  # <-- CORRECT: utils.auth

router = APIRouter()

@router.get("/me")
async def get_current_user_profile(
    current_user: dict = Depends(get_current_user)
):
    """
    Route protégée pour tester l'authentification
    """
    return {
        "message": "Accès autorisé",
        "user_id": current_user.get("user_id"),
        "status": "authenticated"
    }