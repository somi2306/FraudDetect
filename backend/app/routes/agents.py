from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ..core.db import get_db
from ..models.user import User, UserRole
from ..models.bank import Bank
# Import du modèle chèque
from ..models.cheque import Cheque
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


@router.get("/cheques/me")
def get_my_cheques(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    # 1. Récupérer l'ID Clerk
    clerk_id = current_user.get("user_id")

    # 2. Trouver l'agent lié à ce Clerk
    agent = db.query(User).filter(
        User.clerk_id == clerk_id,
        User.role == UserRole.AGENT
    ).first()

    if not agent:
        raise HTTPException(status_code=404, detail="Agent non trouvé")

    if not agent.bank_id:
        raise HTTPException(status_code=400, detail="Aucune banque associée à cet agent.")

    

    # --- FILTRAGE DES CHÈQUES AVEC JOINTURE SUR LE BÉNÉFICIAIRE ---
    beneficiaire_condition = (
        db.query(Cheque)
        .join(User, Cheque.beneficiaire_id == User.id)
        .filter(User.bank_id == agent.bank_id)  # bénéficiaire appartient à l'agence de l’agent
    )

    # 1. Chèques dont la banque cible = banque de l’agent
    cheques_meme_banque = beneficiaire_condition.filter(
        Cheque.banque_cible_id == agent.bank_id
    ).all()

    # 2. Chèques dont la banque cible ≠ banque de l’agent
    cheques_autre_banque = beneficiaire_condition.filter(
        Cheque.banque_cible_id != agent.bank_id
    ).all()

    # --- RETURN ---
    return {
        "agentName": f"{agent.first_name} {agent.last_name}",
        "agentEmail": agent.email,
        "agentBankId": agent.bank_id,
        "cheques_meme_banque": cheques_meme_banque,
        "cheques_autre_banque": cheques_autre_banque,
    }
