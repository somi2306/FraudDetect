from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List

# Imports internes
from ..core.db import get_db
from ..models.user import User, UserRole
from ..models.bank import Bank
from ..models.cheque import Cheque
from ..utils.auth import get_current_user
# Import du gestionnaire WebSocket pour les notifications
from ..services.websocket_manager import manager 

router = APIRouter(
    tags=["Agents Management"]
)

@router.put("/confirm-reset")
def confirm_password_reset(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
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
    clerk_id = current_user.get("user_id")

    agent = db.query(User).filter(
        User.clerk_id == clerk_id,
        User.role == UserRole.AGENT
    ).first()

    if not agent:
        raise HTTPException(status_code=404, detail="Agent non trouvé")

    # --- 1. Chèques INTERNES (Même Banque) ---
    # Chèques déposés par des clients de MA banque
    # Statut : 'pending' ou 'uploaded'
    # Banque Cible : MA banque
    cheques_meme_banque_raw = (
        db.query(Cheque, User)
        .join(User, Cheque.beneficiaire_id == User.id)
        .filter(
            User.bank_id == agent.bank_id,           # Client de ma banque
            Cheque.banque_cible_id == agent.bank_id, # Chèque pour ma banque
            Cheque.status.in_(["pending", "uploaded"])
        )
        .all()
    )

    # --- 2. Chèques EXTERNES (Autre Banque - À Transmettre) ---
    # Chèques déposés par des clients de MA banque
    # Statut : 'pending' ou 'uploaded'
    # Banque Cible : UNE AUTRE banque
    cheques_autre_banque_raw = (
        db.query(Cheque, User)
        .join(User, Cheque.beneficiaire_id == User.id)
        .filter(
            User.bank_id == agent.bank_id,           # Client de ma banque
            Cheque.banque_cible_id != agent.bank_id, # Chèque pour une AUTRE banque
            Cheque.status.in_(["pending", "uploaded"])
        )
        .all()
    )

    # --- 3. Chèques REÇUS (Transmis par d'autres agents) ---
    # C'est la partie manquante !
    # Statut : 'transmitted'
    # Agent Actuel : MOI (l'agent connecté)
    cheques_recus_raw = (
        db.query(Cheque, User)
        .join(User, Cheque.beneficiaire_id == User.id)
        .filter(
            Cheque.agent_actuel_id == agent.id,      # On me l'a assigné
            Cheque.status == "transmitted"           # Il a été transmis
        )
        .all()
    )

    # --- FORMATAGE ---
    
    def format_cheque(cheque, beneficiaire):
        return {
            "cheque": {
                **cheque.__dict__,
                "imageUrl": f"/public/{cheque.image_url}"
            },
            "beneficiaire": {
                "id": beneficiaire.id,
                "name": f"{beneficiaire.first_name} {beneficiaire.last_name}",
                "email": beneficiaire.email
            }
        }

    cheques_meme_banque = [format_cheque(c, u) for c, u in cheques_meme_banque_raw]
    cheques_autre_banque = [format_cheque(c, u) for c, u in cheques_autre_banque_raw]
    
    # On ajoute les chèques reçus à la liste "Même Banque" (ou une nouvelle liste si vous préférez)
    # car ce sont des chèques que je dois traiter maintenant.
    cheques_recus = [format_cheque(c, u) for c, u in cheques_recus_raw]
    
    # Fusion : Les chèques reçus s'ajoutent à ceux que je dois traiter (Même Banque)
    # car techniquement, une fois reçus, ils sont "chez moi" pour traitement.
    cheques_meme_banque.extend(cheques_recus)

    return {
        "agentName": f"{agent.first_name} {agent.last_name}",
        "agentEmail": agent.email,
        "agentBankId": agent.bank_id,
        "cheques_meme_banque": cheques_meme_banque,
        "cheques_autre_banque": cheques_autre_banque,
    }

@router.post("/cheque/transmettre/{cheque_id}")
async def transmettre_cheque(
    cheque_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Transmet un chèque à un agent de la banque cible.
    Envoie une notification WebSocket à l'agent cible.
    """
    clerk_id = current_user.get("user_id")

    # Vérification Agent Expéditeur
    agent = db.query(User).filter(
        User.clerk_id == clerk_id,
        User.role == UserRole.AGENT
    ).first()

    if not agent:
        raise HTTPException(404, "Agent expéditeur non trouvé.")

    # Vérification Chèque
    cheque = db.query(Cheque).filter(Cheque.id == cheque_id).first()
    if not cheque:
        raise HTTPException(404, "Chèque introuvable.")

    # Vérification Logique Métier
    if cheque.banque_cible_id == agent.bank_id:
        raise HTTPException(400, "Ce chèque appartient à votre banque, traitez-le en interne.")

    # Trouver un agent cible dans la banque destinataire
    # (Logique simplifiée : on prend le premier agent disponible de cette banque)
    agent_cible = db.query(User).filter(
        User.bank_id == cheque.banque_cible_id,
        User.role == UserRole.AGENT,
        User.is_active == True
    ).first()

    if not agent_cible:
        raise HTTPException(404, "Aucun agent disponible dans la banque cible pour recevoir ce chèque.")

    # Mise à jour BDD
    cheque.status = "transmitted"
    cheque.agent_actuel_id = agent_cible.id
    db.commit()

    # --- NOTIFICATION WEBSOCKET ---
    try:
        # On notifie l'agent cible (par son clerk_id)
        if agent_cible.clerk_id:
            await manager.send_personal_message(
                {
                    "type": "CHEQUE_RECEIVED",
                    "title": "Chèque Reçu",
                    "message": f"Le chèque #{cheque.id} vous a été transmis pour traitement.",
                    "cheque_id": cheque.id
                },
                agent_cible.clerk_id
            )
            print(f"🔔 Notification envoyée à {agent_cible.email} ({agent_cible.clerk_id})")
    except Exception as e:
        print(f"⚠️ Erreur notification WS: {e}")

    return {"message": f"Chèque transmis avec succès à la banque cible."}

@router.get("/cheques/transmis")
def get_cheques_transmis(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Récupère les chèques qui ont été transmis à cet agent (venant d'autres banques).
    """
    clerk_id = current_user.get("user_id")
    agent = db.query(User).filter(
        User.clerk_id == clerk_id,
        User.role == UserRole.AGENT
    ).first()

    if not agent:
        raise HTTPException(404, "Agent non trouvé")

    cheques = (
        db.query(Cheque)
        .join(User, Cheque.beneficiaire_id == User.id)
        .options(joinedload(Cheque.beneficiaire).joinedload(User.bank))
        .filter(
            Cheque.agent_actuel_id == agent.id,
            Cheque.status == "transmitted"
        )
        .all()
    )

    result = []
    for ch in cheques:
        bank_name = ch.beneficiaire.bank.name if ch.beneficiaire.bank else "Inconnue"
        
        result.append({
            "cheque": {
                "id": ch.id,
                "imageUrl": f"/public/{ch.image_url}",
                "status": ch.status,
                "amount": ch.amount,
                "currency": ch.currency
            },
            "beneficiaire": {
                "id": ch.beneficiaire.id,
                "name": f"{ch.beneficiaire.first_name} {ch.beneficiaire.last_name}",
                "bankName": bank_name
            }
        })
    return result

@router.get("/me")
def get_my_agent(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    clerk_id = current_user.get("user_id")
    if clerk_id is None:
        raise HTTPException(status_code=401, detail="Utilisateur non authentifié")

    agent = db.query(User).filter(
        User.clerk_id == clerk_id,
        User.role == UserRole.AGENT
    ).first()

    if agent is None:
        raise HTTPException(status_code=404, detail="Agent introuvable")

    return {
        "id": agent.id,
        "name": f"{agent.first_name} {agent.last_name}",
        "email": agent.email,
        "bankId": agent.bank_id,
    }

@router.get("/cheques/traites")
def get_cheques_traite(
    current_user: dict = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    clerk_id = current_user.get("user_id")
    agent = db.query(User).filter(
        User.clerk_id == clerk_id,
        User.role == UserRole.AGENT
    ).first()

    cheques = (
        db.query(Cheque)
        .join(User, Cheque.beneficiaire_id == User.id)
        .options(joinedload(Cheque.beneficiaire).joinedload(User.bank))
        .filter(
            Cheque.agent_actuel_id == agent.id, 
            Cheque.status.in_(["rejected", "approved", "validated"])
        )
        .all()
    )

    result = []
    for ch in cheques:
        bank_name = ch.beneficiaire.bank.name if ch.beneficiaire.bank else ""
        result.append({
            "cheque": {
                "id": ch.id,
                "date_depot": ch.date_depot,
                "imageUrl": f"/public/{ch.image_url}",
                "status": ch.status,
                "amount": ch.amount
            },
            "beneficiaire": {
                "id": ch.beneficiaire.id,
                "name": f"{ch.beneficiaire.first_name} {ch.beneficiaire.last_name}",
                "bankName": bank_name
            }
        })

    return result