from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..core.db import get_db
from ..models.user import User, UserRole
from ..utils.auth import get_current_user # Nécessaire pour identifier l'agent via son token Clerk

router = APIRouter(
    tags=["Agents Management"]
)

# NOTE: La route /login n'existe plus ici car l'authentification est gérée par Clerk (Frontend).
# Le backend reçoit uniquement des requêtes avec un Token valide via 'get_current_user'.

@router.put("/confirm-reset")
def confirm_password_reset(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Appelé par le Frontend une fois que l'agent a changé son mot de passe sur Clerk.
    Cette route passe le flag 'must_reset_password' à False dans la base locale.
    """
    clerk_id = current_user.get("user_id")

    # 1. Retrouver l'agent grâce à son ID Clerk (issu du token)
    agent = db.query(User).filter(User.clerk_id == clerk_id).first()

    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Agent non trouvé."
        )

    # 2. Vérification de sécurité : S'assurer que c'est bien un Agent
    if agent.role != UserRole.AGENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cette action est réservée aux agents."
        )
        
    # 3. Mettre à jour le statut
    # On considère que si cette route est appelée, c'est que user.updatePassword() a réussi côté Frontend
    agent.must_reset_password = False
    
    db.commit()
    db.refresh(agent)
    
    return {"status": "success", "message": "Réinitialisation confirmée, accès au dashboard débloqué."}