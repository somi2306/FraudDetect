
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..utils.security import verify_password, get_password_hash, create_access_token
from ..core.db import get_db
from ..models.user import User, UserRole
from ..utils.security import verify_password, get_password_hash # Import des fonctions de hachage
from ..schemas.agent_schemas import AgentLogin, AgentPasswordReset # Import des schémas

router = APIRouter(
   
    tags=["Agents Authentication"]
)

@router.post("/login")
def agent_login(agent_data: AgentLogin, db: Session = Depends(get_db)):
    """
    Authentifie l'Agent par email et mot de passe. 
    Vérifie si une réinitialisation de mot de passe est requise.
    """
    # 1. Rechercher l'utilisateur Agent par email
    agent = db.query(User).filter(User.email == agent_data.email).first()

    if not agent or agent.role != UserRole.AGENT:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Identifiants invalides ou rôle non autorisé.",
        )

    # 2. Vérifier le mot de passe
    if not verify_password(agent_data.password, agent.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Identifiants invalides.",
        )

    # 3. Vérifier l'obligation de réinitialisation
    if agent.must_reset_password:
        return {
            "status": "reset_required",
            "message": "Veuillez modifier votre mot de passe à la première connexion.",
            # En production, vous renverriez un jeton temporaire ici
        }

    # 4. Connexion réussie (si must_reset_password est False)
    access_token = create_access_token(
        data={"sub": agent.email, "role": agent.role.value, "user_id": agent.id}
    )
    # TODO: Ajouter la logique de génération de jeton JWT ici pour l'authentification
    return {"status": "success",
            "message": "Connexion Agent réussie.",
            "access_token": access_token,
            "user_id": agent.id}

@router.post("/reset-password")
def agent_reset_password(reset_data: AgentPasswordReset, db: Session = Depends(get_db)):
    """
    Permet à l'Agent de modifier son mot de passe après la première connexion.
    """
    agent = db.query(User).filter(User.email == reset_data.email, User.role == UserRole.AGENT).first()

    if not agent:
        raise HTTPException(status_code=404, detail="Agent non trouvé.")
    
    # 1. Vérifier l'ancien mot de passe
    if not verify_password(reset_data.old_password, agent.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Ancien mot de passe incorrect.",
        )
        
    # 2. Hacher et mettre à jour le nouveau mot de passe
    agent.hashed_password = get_password_hash(reset_data.new_password)
    agent.must_reset_password = False  # Désactiver le drapeau de réinitialisation
    
    db.add(agent)
    db.commit()
    db.refresh(agent)
    
    return {"status": "success", "message": "Mot de passe modifié avec succès."}