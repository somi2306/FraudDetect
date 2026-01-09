from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from ..core.db import get_db
from ..utils.auth import get_current_user
from ..models.user import User, UserRole
from ..schemas.user import UserSync
from ..services.clerk_sync_service import upsert_clerk_user
from ..utils.bank_codes import get_bank_id_from_code

# Fonction utilitaire pour normaliser le rôle
def _normalize_role(value):
    if not value: return "BENEFICIAIRE"
    lookup = {"bénéficiaire": "BENEFICIAIRE", "agent": "AGENT", "admin": "ADMIN"}
    key = str(value.value).strip().lower() if hasattr(value, "value") else str(value).strip().lower()
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
        raise HTTPException(status_code=401, detail="Token invalide")

    print(f"🔍 DEBUG CALLBACK - Reçu: CIN={user_data.cin}, RIB={user_data.rib}, BankCode={user_data.bank_code}")

    try:
        db_user = db.query(User).filter(User.clerk_id == clerk_id).first()
        
        user_role_to_return = None
        must_reset = False
        bank_id = None

        if db_user:
            # --- MISE À JOUR ---
            # Vérifications d'unicité en cas de changement
            if user_data.cin and user_data.cin != db_user.cin:
                if db.query(User).filter(User.cin == user_data.cin).first():
                    raise HTTPException(status_code=400, detail="Ce CIN est déjà utilisé par un autre compte.")
            
            db_user.first_name = user_data.firstName
            db_user.last_name = user_data.lastName
            db_user.image_url = user_data.imageUrl
            db_user.email = user_data.email
            
            # Remplissage des données manquantes (cas du "Fantôme")
            if user_data.cin and not db_user.cin:
                db_user.cin = user_data.cin
            
            if user_data.rib and not db_user.rib:
                db_user.rib = user_data.rib
            
            # Gestion Banque
            if user_data.bank_code and not db_user.bank_id:
                try:
                    # On force la conversion int -> int pour être sûr
                    bid = get_bank_id_from_code(user_data.bank_code)
                    db_user.bank_id = bid
                    print(f"🏦 Banque mise à jour pour {clerk_id}: Code {user_data.bank_code} -> ID {bid}")
                except ValueError as e:
                    print(f"⚠️ Erreur Banque (Update): {e}")

            user_role_to_return = db_user.role
            must_reset = db_user.must_reset_password
            bank_id = db_user.bank_id
            
        else:
            # --- CRÉATION ---
            if not user_data.cin or not user_data.rib:
                raise HTTPException(status_code=400, detail="CIN et RIB sont obligatoires pour l'inscription.")

            if db.query(User).filter(User.cin == user_data.cin).first():
                raise HTTPException(status_code=400, detail="Ce CIN est déjà utilisé.")

            # Gestion Banque
            bank_id_value = None
            if user_data.bank_code:
                try:
                    bank_id_value = get_bank_id_from_code(user_data.bank_code)
                    print(f"🏦 Banque trouvée pour création: Code '{user_data.bank_code}' -> ID {bank_id_value}")
                except ValueError as e:
                    # IMPORTANT: On ne bloque pas l'inscription, mais on log l'erreur
                    print(f"❌ ERREUR CRITIQUE BANQUE: {e}")
                    # Optionnel: raise HTTPException(400, detail="Banque non reconnue") 
            else:
                print("⚠️ Aucun code banque fourni dans le payload user_data")

            new_user = User(
                clerk_id=clerk_id,
                email=user_data.email,
                first_name=user_data.firstName,
                last_name=user_data.lastName,
                image_url=user_data.imageUrl,
                cin=user_data.cin,
                rib=user_data.rib,
                bank_id=bank_id_value,
                role=UserRole.BENEFICIAIRE,
                must_reset_password=False
            )
            db.add(new_user)
            user_role_to_return = UserRole.BENEFICIAIRE
            bank_id = bank_id_value # Pour le retour

        try:
            db.commit()
        except IntegrityError as e:
            db.rollback()
            err_msg = str(e.orig)
            if "ix_users_cin" in err_msg:
                raise HTTPException(400, "Ce CIN existe déjà (doublon).")
            elif "ix_users_rib" in err_msg:
                raise HTTPException(400, "Ce RIB existe déjà (doublon).")
            raise HTTPException(400, "Erreur de doublon (Données uniques requises).")

        # Sync Supabase (Code existant inchangé, simplifié ici)
        try:
            role_val = _normalize_role(user_role_to_return)
            payload = {
                "clerk_id": clerk_id, "email": user_data.email, "role": role_val,
                "first_name": user_data.firstName, "last_name": user_data.lastName, "image_url": user_data.imageUrl
            }
            upsert_clerk_user({k:v for k,v in payload.items() if v})
        except Exception as e:
            print(f"⚠️ Erreur Sync Supabase: {e}")

        return {
            "status": "success",
            "clerk_id": clerk_id,
            "role": user_role_to_return,
            "must_reset_password": must_reset,
            "bank_id": bank_id
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"🔥 Erreur Serveur Auth: {e}")
        raise HTTPException(status_code=500, detail=str(e))