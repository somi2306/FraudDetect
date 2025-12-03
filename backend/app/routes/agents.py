from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ..core.db import get_db
from ..models.user import User, UserRole
from ..models.bank import Bank
# Assurez-vous d'importer votre modèle Cheque (si fusionné depuis l'autre branche)
# from ..models.cheque import Cheque 
from ..utils.auth import get_current_user

router = APIRouter(
    tags=["Agents Management"]
)

@router.put("/confirm-reset")
def confirm_password_reset(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    # ... (Garder votre code existant pour le reset ici) ...
    clerk_id = current_user.get("user_id")
    agent = db.query(User).filter(User.clerk_id == clerk_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent non trouvé.")
    agent.must_reset_password = False
    db.commit()
    return {"status": "success"}


# --- NOUVELLE ROUTE POUR LE DASHBOARD ---
@router.get("/cheques/me")
def get_agent_dashboard_data(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Renvoie les données du dashboard pour l'agent connecté via Clerk.
    """
    clerk_id = current_user.get("user_id")
    
    # 1. Récupérer l'agent
    agent = db.query(User).filter(User.clerk_id == clerk_id).first()
    if not agent or agent.role != UserRole.AGENT:
        raise HTTPException(status_code=403, detail="Accès réservé aux agents.")

    if not agent.bank_id:
        raise HTTPException(status_code=400, detail="Aucune banque associée à cet agent.")

    # 2. Récupérer les chèques (LOGIQUE DE L'AUTRE BRANCHE ADAPTÉE)
    # Note : Je simule ici la récupération car je n'ai pas le fichier models/cheque.py complet
    # Vous devrez décommenter et adapter selon votre modèle Cheque réel
    
    # from ..models.cheque import Cheque
    
    # cheques_meme_banque_db = db.query(Cheque).filter(Cheque.bank_id == agent.bank_id).all()
    # cheques_autre_banque_db = db.query(Cheque).filter(Cheque.bank_id != agent.bank_id).all() # Simplifié

    # Pour le test, je renvoie des données vides ou simulées si la table n'est pas prête
    cheques_meme_banque = [] 
    cheques_autre_banque = []

    return {
        "agentName": f"{agent.first_name} {agent.last_name}",
        "agentEmail": agent.email,
        "agentBankId": agent.bank_id,
        "cheques_meme_banque": cheques_meme_banque,
        "cheques_autre_banque": cheques_autre_banque,
        "beneficiaireName": "" # Champ legacy
    }