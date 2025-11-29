# backend/app/schemas/agent_schemas.py

from pydantic import BaseModel, EmailStr

# Schéma pour la connexion de l'Agent
class AgentLogin(BaseModel):
    """
    Données nécessaires à la connexion d'un Agent (Email et Mot de passe).
    """
    email: EmailStr
    password: str

# Schéma pour la modification du mot de passe
class AgentPasswordReset(BaseModel):
    """
    Données nécessaires pour la réinitialisation forcée du mot de passe.
    """
    email: EmailStr
    old_password: str
    new_password: str