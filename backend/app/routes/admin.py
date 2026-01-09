from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import List, Optional
import random
import string

# Imports internes
from ..core.db import get_db
from ..models.user import User, UserRole
from ..models.bank import Bank
from ..models.cheque import Cheque # Import du modèle Cheque pour les stats
from ..utils.auth import get_current_user
from ..services.clerk_service import (
    create_clerk_user, 
    update_clerk_user, 
    toggle_clerk_ban, 
    set_clerk_password
)
from ..utils.email_service import (
    send_agent_welcome_email, 
    send_account_status_email, 
    send_password_reset_email,
    send_beneficiary_status_email # Import de l'email spécifique bénéficiaire
)

router = APIRouter(
    tags=["Admin Management"]
)

# --- SCHÉMAS PYDANTIC ---

class BankResponse(BaseModel):
    id: int
    name: str
    class Config:
        from_attributes = True

class CreateAgentRequest(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr          
    personal_email: EmailStr 
    password: str
    bank_id: int

class UpdateAgentRequest(BaseModel):
    first_name: str
    last_name: str

class AgentResponse(BaseModel):
    id: int
    clerk_id: Optional[str] = None 
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    bank_name: Optional[str] = None
    is_active: bool
    class Config:
        from_attributes = True

class BeneficiaryResponse(BaseModel):
    id: int
    clerk_id: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    cin: Optional[str] = None
    rib: Optional[str] = None
    is_active: bool
    
    # Champs calculés pour les statistiques
    total_cheques: int = 0
    rejected_cheques: int = 0
    
    class Config:
        from_attributes = True

# --- ROUTES BANQUES & AGENTS ---

@router.get("/banks", response_model=List[BankResponse])
def get_banks(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    return db.query(Bank).all()

@router.get("/agents", response_model=List[AgentResponse])
def get_all_agents(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    agents = db.query(User).filter(User.role == UserRole.AGENT).all()
    
    result = []
    for a in agents:
        bank_name = a.bank.name if a.bank else "Aucune"
        result.append({
            "id": a.id,
            "clerk_id": a.clerk_id,
            "first_name": a.first_name,
            "last_name": a.last_name,
            "email": a.email,
            "bank_name": bank_name,
            "is_active": a.is_active
        })
    return result

@router.post("/create-agent")
async def create_agent(
    agent_data: CreateAgentRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    if db.query(User).filter(User.email == agent_data.email).first():
        raise HTTPException(status_code=400, detail="Cet email professionnel est déjà utilisé.")

    try:
        # Création Clerk
        clerk_user = await create_clerk_user(
            email=agent_data.email,
            password=agent_data.password,
            first_name=agent_data.first_name,
            last_name=agent_data.last_name
        )
        clerk_id = clerk_user["id"]

        # Création DB Locale
        new_agent = User(
            clerk_id=clerk_id,
            email=agent_data.email,
            personal_email=agent_data.personal_email,
            first_name=agent_data.first_name,
            last_name=agent_data.last_name,
            role=UserRole.AGENT,
            bank_id=agent_data.bank_id,
            must_reset_password=True,
            is_active=True,
            image_url=clerk_user.get("image_url") 
        )
        
        db.add(new_agent)
        db.commit()
        db.refresh(new_agent)
        
        # Email de Bienvenue
        background_tasks.add_task(
            send_agent_welcome_email, 
            to_email=agent_data.personal_email, 
            login_email=agent_data.email,       
            first_name=agent_data.first_name, 
            temp_password=agent_data.password
        )
        
        return {"message": "Agent créé avec succès.", "agent_id": new_agent.id}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/agents/{agent_id}")
async def update_agent(
    agent_id: int,
    data: UpdateAgentRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    agent = db.query(User).filter(User.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent non trouvé")

    is_mock = not agent.clerk_id or agent.clerk_id.startswith("user_mock_")
    
    if not is_mock:
        try:
            await update_clerk_user(agent.clerk_id, data.first_name, data.last_name)
        except Exception as e:
            print(f"⚠️ Avertissement: Échec mise à jour Clerk ({e}). Continuation locale.")

    try:
        agent.first_name = data.first_name
        agent.last_name = data.last_name
        db.commit()
        return {"message": "Informations mises à jour"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur DB: {str(e)}")

@router.put("/agents/{agent_id}/status")
async def toggle_agent_status(
    agent_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    agent = db.query(User).filter(User.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent non trouvé")

    new_status = not agent.is_active
    
    is_mock = not agent.clerk_id or agent.clerk_id.startswith("user_mock_")
    if not is_mock:
        try:
            await toggle_clerk_ban(agent.clerk_id, ban=(not new_status))
        except Exception as e:
            print(f"⚠️ Avertissement: Échec Ban Clerk ({e}). Continuation locale.")

    agent.is_active = new_status
    db.commit()
    
    # Notification Agent (Email Perso > Pro)
    target_email = agent.personal_email if agent.personal_email else agent.email
    if target_email:
        background_tasks.add_task(
            send_account_status_email, # Template pour AGENT
            to_email=target_email,
            first_name=agent.first_name,
            is_active=new_status
        )
    
    status_str = "activé" if new_status else "désactivé"
    return {"message": f"Compte agent {status_str}", "is_active": new_status}

@router.post("/agents/{agent_id}/reset-password")
async def reset_agent_password_admin(
    agent_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    agent = db.query(User).filter(User.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent non trouvé")
    
    is_mock = not agent.clerk_id or agent.clerk_id.startswith("user_mock_")
    if is_mock:
        raise HTTPException(
            status_code=400, 
            detail="Impossible de réinitialiser le mot de passe d'un agent de test (Mock)."
        )

    chars = string.ascii_letters + string.digits + "!@#$%"
    temp_password = "".join(random.choice(chars) for _ in range(12))

    try:
        await set_clerk_password(agent.clerk_id, temp_password)
        agent.must_reset_password = True
        db.commit()
        
        target_email = agent.personal_email if agent.personal_email else agent.email
        
        # Envoi Synchrone pour confirmation Admin
        email_sent = send_password_reset_email(
            to_email=target_email, 
            login_email=agent.email,
            first_name=agent.first_name,
            temp_password=temp_password
        )

        message = "Mot de passe réinitialisé."
        if not email_sent:
            message += " MAIS l'envoi de l'email a échoué."

        return {
            "message": message, 
            "temp_password": temp_password,
            "email_sent": email_sent,
            "target_email": target_email
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# --- ROUTES BÉNÉFICIAIRES ---

@router.get("/beneficiaries", response_model=List[BeneficiaryResponse])
def get_all_beneficiaries(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Liste les bénéficiaires avec leurs statistiques de chèques.
    """
    beneficiaries = db.query(User).filter(User.role == UserRole.BENEFICIAIRE).all()
    
    result = []
    for user in beneficiaries:
        # Calcul des stats sur la table Cheque
        total_cheques = db.query(Cheque).filter(Cheque.beneficiaire_id == user.id).count()
        rejected_cheques = db.query(Cheque).filter(
            Cheque.beneficiaire_id == user.id, 
            Cheque.status == "rejected"
        ).count()
        
        result.append({
            "id": user.id,
            "clerk_id": user.clerk_id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "cin": user.cin,
            "rib": user.rib,
            "is_active": user.is_active,
            "total_cheques": total_cheques,
            "rejected_cheques": rejected_cheques
        })
        
    return result

@router.put("/beneficiaries/{user_id}/status")
async def toggle_beneficiary_status(
    user_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Bénéficiaire non trouvé")

    new_status = not user.is_active
    
    is_mock = not user.clerk_id or user.clerk_id.startswith("user_mock_")
    if not is_mock:
        try:
            await toggle_clerk_ban(user.clerk_id, ban=(not new_status))
        except Exception as e:
            print(f"⚠️ Avertissement: Échec Ban Clerk ({e}).")

    user.is_active = new_status
    db.commit()
    
    # Notification Bénéficiaire (Email standard)
    target_email = user.email 
    if target_email:
        background_tasks.add_task(
            send_beneficiary_status_email, # Template pour BÉNÉFICIAIRE
            to_email=target_email,
            first_name=user.first_name,
            is_active=new_status
        )
    
    status_str = "activé" if new_status else "désactivé"
    return {"message": f"Compte bénéficiaire {status_str}", "is_active": new_status}