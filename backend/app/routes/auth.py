# backend/app/routers/auth.py
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

# Imports depuis notre application
from ..core.db import get_db
from ..utils.auth import get_current_user
from ..models.user import User, UserRole  # Assurez-vous d'importer UserRole
from ..schemas.user import UserSync       # Le schéma mis à jour (sans 'role')

router = APIRouter()

@router.post("/callback")
async def auth_callback(
    user_data: UserSync,
    request: Request,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    clerk_id = current_user.get("user_id")
    if not clerk_id:
        raise HTTPException(status_code=401, detail="Utilisateur non valide depuis le token")

    try:
        # 1. Vérifier si l'utilisateur existe
        db_user = db.query(User).filter(User.clerk_id == clerk_id).first()
        
        user_role_to_return = None

        if db_user:
            # 2. L'utilisateur existe, on le MET À JOUR (infos de base)
            db_user.first_name = user_data.firstName
            db_user.last_name = user_data.lastName
            db_user.image_url = user_data.imageUrl
            db_user.email = user_data.email
            
            # On ne met à jour ni CIN, ni RIB, ni Rôle pour un utilisateur existant
            # Ces infos sont fixées à la création
            print(f"Utilisateur mis à jour : {clerk_id}")
            user_role_to_return = db_user.role # On récupère le rôle existant
        
        else:
            # 3. L'utilisateur n'existe pas, on le CRÉE
            
            # Validation des données supplémentaires (POUR LA CRÉATION)
            if not user_data.cin:
                raise HTTPException(status_code=400, detail="Le CIN est obligatoire")
            if not user_data.rib:
                raise HTTPException(status_code=400, detail="Le RIB est obligatoire")

            # Vérifier si le CIN ou RIB existe déjà
            existing_cin = db.query(User).filter(User.cin == user_data.cin).first()
            if existing_cin:
                raise HTTPException(status_code=400, detail="Ce CIN est déjà utilisé")

            existing_rib = db.query(User).filter(User.rib == user_data.rib).first()
            if existing_rib:
                raise HTTPException(status_code=400, detail="Ce RIB est déjà utilisé")

            new_user = User(
                clerk_id=clerk_id,
                email=user_data.email,
                first_name=user_data.firstName,
                last_name=user_data.lastName,
                image_url=user_data.imageUrl,
                cin=user_data.cin,
                rib=user_data.rib,
                role=UserRole.BENEFICIAIRE  # <-- RÔLE DÉFINI PAR DÉFAUT ICI
            )
            db.add(new_user)
            print(f"Nouvel utilisateur créé : {clerk_id}")
            user_role_to_return = UserRole.BENEFICIAIRE # On définit le nouveau rôle

        db.commit()
        return {
            "status": "success",
            "message": "Utilisateur synchronisé",
            "clerk_id": clerk_id,
            "role": user_role_to_return # On retourne le rôle (nouveau ou existant)
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Erreur SQLAlchemy: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur de base de données: {str(e)}")