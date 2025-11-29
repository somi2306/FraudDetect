# backend/app/models/user.py
from sqlalchemy import String, Integer, Enum as SQLEnum,Boolean,ForeignKey
from sqlalchemy.orm import Mapped ,relationship
from sqlalchemy.orm import mapped_column
from typing import Optional
from enum import Enum
from ..core.db import Base 

class UserRole(str, Enum):
    ADMIN = "Admin"
    AGENT = "Agent"
    BENEFICIAIRE = "Bénéficiaire"

from app.models.bank import Bank

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    clerk_id: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=True)#j'ai modifier nullable en true pour les agent car il ne l'utilise pas 
    hashed_password: Mapped[Optional[str]] = mapped_column(String, nullable=True) #j'ai ajouter cela pour le hash de mot de passe pour l'agent
    must_reset_password: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)#pour forcer l'initialisation de mot de passe pour l'agent
    email: Mapped[Optional[str]] = mapped_column(String, unique=True, index=True)
    first_name: Mapped[Optional[str]] = mapped_column(String)
    last_name: Mapped[Optional[str]] = mapped_column(String)
    image_url: Mapped[Optional[str]] = mapped_column(String)
    cin: Mapped[Optional[str]] = mapped_column(String, unique=True, index=True)
    rib: Mapped[Optional[str]] = mapped_column(String, unique=True, index=True)
    role: Mapped[UserRole] = mapped_column(SQLEnum(UserRole), nullable=False)
    
    bank_id: Mapped[Optional[int]] = mapped_column(ForeignKey("banks.id"), nullable=True) # pour la banque de l'agent :Clé étrangère pointant vers l'ID de la banque
    
    bank: Mapped[Optional["Bank"]] = relationship(back_populates="users") # Relation (permet d'accéder aux détails de la banque depuis l'utilisateur