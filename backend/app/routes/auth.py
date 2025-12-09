# backend/app/routes/auth.py
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

# Imports depuis notre application
from ..core.db import get_db
from ..utils.auth import get_current_user
from ..models.user import User, UserRole
from ..schemas.user import UserSync
from ..services.clerk_sync_service import upsert_clerk_user

# Fonction utilitaire pour normaliser le rôle avant envoi à Supabase
def _normalize_role(value):
    if not value:
        return "BENEFICIAIRE"
    lookup = {
        "bénéficiaire": "BENEFICIAIRE",
        "beneficiaire": "BENEFICIAIRE",
        "beneficiary": "BENEFICIAIRE",
        "agent": "AGENT",
        "admin": "ADMIN",
    }
    # Si c'est un Enum, on prend sa value
    if hasattr(value, "value"):
        key = str(value.value).strip().lower()
    else:
        key = str(value).strip().lower()
        
    return lookup.get(key, "BENEFICIAIRE")

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
        # 1. Vérifier si l'utilisateur existe en base locale
        db_user = db.query(User).filter(User.clerk_id == clerk_id).first()
        
        user_role_to_return = None
        must_reset = False
        bank_id = None

        if db_user:
            # 2. L'utilisateur existe (Cas Admin, Agent, ou Bénéficiaire déjà inscrit)
            # On met à jour les infos de base
            db_user.first_name = user_data.firstName
            db_user.last_name = user_data.lastName
            db_user.image_url = user_data.imageUrl
            db_user.email = user_data.email
            
            # On récupère les infos critiques
            user_role_to_return = db_user.role
            must_reset = db_user.must_reset_password
            bank_id = db_user.bank_id
            
            print(f"Utilisateur synchronisé : {clerk_id} | Role: {user_role_to_return}")
        
        else:
            # 3. L'utilisateur n'existe pas (Cas Inscription Bénéficiaire)
            if not user_data.cin:
                raise HTTPException(status_code=400, detail="Le CIN est obligatoire")
            if not user_data.rib:
                raise HTTPException(status_code=400, detail="Le RIB est obligatoire")

            # Vérifications d'unicité
            if db.query(User).filter(User.cin == user_data.cin).first():
                raise HTTPException(status_code=400, detail="Ce CIN est déjà utilisé")
            if db.query(User).filter(User.rib == user_data.rib).first():
                raise HTTPException(status_code=400, detail="Ce RIB est déjà utilisé")

            new_user = User(
                clerk_id=clerk_id,
                email=user_data.email,
                first_name=user_data.firstName,
                last_name=user_data.lastName,
                image_url=user_data.imageUrl,
                cin=user_data.cin,
                rib=user_data.rib,
                role=UserRole.BENEFICIAIRE, # Par défaut
                must_reset_password=False
            )
            db.add(new_user)
            user_role_to_return = UserRole.BENEFICIAIRE
            print(f"Nouvel utilisateur créé : {clerk_id}")

        db.commit()

        # --- 4. Synchronisation Supabase (Pour la fonctionnalité Chèques) ---
        # On synchronise aussi vers la table publique 'users' de Supabase
        # pour que l'OCR et les triggers fonctionnent.
        
        role_value = _normalize_role(user_role_to_return)

        supabase_payload = {
            "clerk_id": clerk_id,
            "email": user_data.email,
            "first_name": user_data.firstName,
            "last_name": user_data.lastName,
            "image_url": user_data.imageUrl,
            "role": role_value,
        }

        # On nettoie les valeurs None
        sanitized_payload = {k: v for k, v in supabase_payload.items() if v is not None}
        
        try:
            upsert_clerk_user(sanitized_payload)
        except Exception as e:
            print(f"⚠️ Erreur sync Supabase (non-bloquant): {e}")

        # --- 5. Retour vers le Frontend ---
        return {
            "status": "success",
            "message": "Utilisateur synchronisé",
            "clerk_id": clerk_id,
            "role": user_role_to_return,
            "must_reset_password": must_reset, # Important pour Agent
            "bank_id": bank_id                 # Important pour Agent
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Erreur SQLAlchemy: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur de base de données: {str(e)}")