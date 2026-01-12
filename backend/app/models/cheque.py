# backend/app/models/cheque.py

from sqlalchemy import String, Integer, Float, DateTime, ForeignKey, Enum as SQLAlchemyEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from typing import Optional
import enum

from ..core.db import Base
# (Gardes tes autres imports User, Bank...)

# 1. Définition de l'Enum
class CheckStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    TRANSMITTED = "transmitted"
    # Ajoute 'uploaded' si tu l'utilises parfois, sinon 'pending' suffit
    UPLOADED = "uploaded" 

class Cheque(Base):
    __tablename__ = "cheques"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    image_url: Mapped[str] = mapped_column(String, nullable=False)
    
    # 2. Utilisation de l'Enum ici
    status: Mapped[CheckStatus] = mapped_column(String, default=CheckStatus.PENDING)

    date_depot: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    beneficiaire_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    beneficiaire = relationship("User", foreign_keys=[beneficiaire_id])
    
    banque_cible_id: Mapped[int] = mapped_column(ForeignKey("banks.id"), nullable=False)
    
    agent_actuel_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)