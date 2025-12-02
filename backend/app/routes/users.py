from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..core.db import get_db
from ..models.user import User
from ..utils.auth import get_current_user

router = APIRouter()

@router.get("/me")
async def get_current_user_profile(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    # Récupérer l'utilisateur complet depuis la DB pour avoir son rôle
    user = db.query(User).filter(User.clerk_id == current_user["user_id"]).first()
    
    if not user:
         return {"error": "User not found"}

    return {
        "user_id": user.clerk_id,
        "role": user.role,           # <--- On ajoute le rôle ici
        "bank_id": user.bank_id,     # Utile pour les agents
        "first_name": user.first_name,
        "last_name": user.last_name
    }