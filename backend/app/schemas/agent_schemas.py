from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime

# --- On garde ces schémas pour la structure des données ---

class ChequeSchema(BaseModel):
    id: int
    amount: float
    beneficiaireName: str
    status: str
    date: datetime
    # Ajoutez d'autres champs selon votre modèle Cheque réel
    
    class Config:
        from_attributes = True

class AgentDashboardData(BaseModel):
    agentName: str
    agentEmail: str
    agentBankId: int
    cheques_meme_banque: List[ChequeSchema]
    cheques_autre_banque: List[ChequeSchema]