
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..utils.security import verify_password, get_password_hash, create_access_token
from ..core.db import get_db
from ..models.user import User, UserRole
from ..models.cheque import Cheque
from ..utils.security import verify_password, get_password_hash # Import des fonctions de hachage
from ..schemas.agent_schemas import AgentLogin, AgentPasswordReset # Import des schémas
from fastapi.security import OAuth2PasswordBearer
from ..utils.security import decode_access_token  
from fastapi import Depends, Header
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
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/agent/login")




@router.get("/cheques/me")
def get_my_cheques(authorization: str = Header(...), db: Session = Depends(get_db)):
    # ... (Partie authentification de l'agent inchangée)
    token = authorization.split(" ")[1]
    payload = decode_access_token(token)
    agent_id = payload.get("user_id")

    # Rechercher l'agent
    agent = db.query(User).filter(User.id == agent_id, User.role == UserRole.AGENT).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent non trouvé")

    beneficiaire_condition = db.query(Cheque).join(
        User, Cheque.beneficiaire_id == User.id # Supposition: le chèque a un beneficiaire_id
    ).filter(
        User.bank_id == agent.bank_id # Le bénéficiaire doit appartenir à la banque de l'agent
    )

    # 1. Chèques de la même banque cible QUE L'AGENT (et bénéficiaire dans la même banque)
    cheques_meme_banque = beneficiaire_condition.filter(
        Cheque.banque_cible_id == agent.bank_id
    ).all()

    # 2. Chèques d'une autre banque cible QUE L'AGENT (et bénéficiaire dans la même banque)
    cheques_autre_banque = beneficiaire_condition.filter(
        Cheque.banque_cible_id != agent.bank_id
    ).all()
    
    # --- FIN DU NOUVEAU FILTRAGE ---

    return {
        "cheques_meme_banque": cheques_meme_banque,
        "cheques_autre_banque": cheques_autre_banque,
        "agentName": agent.first_name + " " + agent.last_name,
        "agentBankId": agent.bank_id,
        "agentEmail":agent.email
    }
