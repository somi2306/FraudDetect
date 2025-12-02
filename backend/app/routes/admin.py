from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import List

# Imports internes
from ..core.db import get_db
from ..models.user import User, UserRole
from ..models.bank import Bank
from ..utils.auth import get_current_user
from ..services.clerk_service import create_clerk_user
from ..utils.email_service import send_agent_welcome_email

router = APIRouter(
    tags=["Admin Management"]
)

# --- Schémas Pydantic ---
class BankResponse(BaseModel):
    id: int
    name: str
    class Config:
        from_attributes = True

class CreateAgentRequest(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr         # Email PRO (Identifiant Clerk)
    personal_email: EmailStr # <--- NOUVEAU : Email PERSO (Pour recevoir le mot de passe)
    password: str
    bank_id: int

# --- Routes ---

@router.get("/banks", response_model=List[BankResponse])
def get_banks(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Récupère la liste de toutes les banques.
    """
    banks = db.query(Bank).all()
    return banks

@router.post("/create-agent")
async def create_agent(
    agent_data: CreateAgentRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Crée un agent et envoie les identifiants sur son EMAIL PERSONNEL.
    """
    
    # 1. Vérifier si l'email PRO existe déjà
    existing_user = db.query(User).filter(User.email == agent_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=400, 
            detail="L'email professionnel est déjà utilisé."
        )

    try:
        # 2. Création Clerk (Avec l'email PRO comme identifiant)
        clerk_user = await create_clerk_user(
            email=agent_data.email, 
            password=agent_data.password,
            first_name=agent_data.first_name,
            last_name=agent_data.last_name
        )
        clerk_id = clerk_user["id"]

        # 3. Création DB Locale
        new_agent = User(
            clerk_id=clerk_id,
            email=agent_data.email, # On stocke l'email pro en base
            first_name=agent_data.first_name,
            last_name=agent_data.last_name,
            role=UserRole.AGENT,
            bank_id=agent_data.bank_id,
            must_reset_password=True,
            image_url=clerk_user.get("image_url") 
        )
        
        db.add(new_agent)
        db.commit()
        db.refresh(new_agent)
        
        # 4. Envoi de l'email sur l'adresse PERSONNELLE
        # 4. Envoi de l'email sur l'adresse PERSONNELLE
        background_tasks.add_task(
            send_agent_welcome_email, 
            to_email=agent_data.personal_email,  # Destinataire (Perso)
            login_email=agent_data.email,        # Identifiant à afficher (Pro) <--- AJOUTÉ
            first_name=agent_data.first_name, 
            temp_password=agent_data.password
        )
        
        return {
            "message": f"Agent créé. Les identifiants ont été envoyés à {agent_data.personal_email}.", 
            "agent_id": new_agent.id
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))