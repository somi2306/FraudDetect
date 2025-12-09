# backend/app/routes/users.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List

# Imports internes
from ..core.db import get_db
from ..models.user import User
from ..utils.auth import get_current_user

router = APIRouter()

# --- SCHEMAS ---
class ProfileUpdate(BaseModel):
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    imageUrl: Optional[str] = None

# --- ROUTES ---

@router.get("/me")
async def get_current_user_profile(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Récupère le profil complet de l'utilisateur connecté.
    Utilisé par le Frontend pour déterminer le rôle et l'accès.
    """
    # On utilise l'ID Clerk pour trouver l'utilisateur en base locale
    user = db.query(User).filter(User.clerk_id == current_user["user_id"]).first()
    
    if not user:
         raise HTTPException(status_code=404, detail="Utilisateur non trouvé en base de données.")

    # On renvoie un objet complet fusionnant les besoins Admin/Agent et Profil
    return {
        "user_id": user.clerk_id,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "image_url": user.image_url,
        
        # Champs critiques pour la logique métier
        "role": user.role,           
        "bank_id": user.bank_id,     # Pour les Agents
        "must_reset_password": user.must_reset_password,
        
        # Champs spécifiques bénéficiaires
        "cin": user.cin,
        "rib": user.rib
    }

@router.put("/profile")
async def update_profile(
    profile_data: ProfileUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Met à jour les informations du profil (Nom, Prénom, Image).
    Appelé depuis la page de profil.
    """
    clerk_id = current_user.get("user_id")
    if not clerk_id:
        raise HTTPException(status_code=401, detail="Non authentifié")

    db_user = db.query(User).filter(User.clerk_id == clerk_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

    if profile_data.firstName is not None:
        db_user.first_name = profile_data.firstName
    if profile_data.lastName is not None:
        db_user.last_name = profile_data.lastName
    if profile_data.imageUrl is not None:
        db_user.image_url = profile_data.imageUrl

    db.commit()
    db.refresh(db_user)

    return {"status": "success", "message": "Profil mis à jour"}

# --- ROUTES SESSION (Placeholders pour future implémentation Clerk) ---

@router.get("/sessions")
async def get_user_sessions(
    current_user: dict = Depends(get_current_user),
):
    """Récupère les sessions actives (Géré par Clerk en réalité)"""
    return []

@router.delete("/sessions/{session_id}")
async def revoke_session(
    session_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Révoque une session"""
    return {"status": "success", "message": f"Session {session_id} révoquée"}