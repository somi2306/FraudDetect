from sqlalchemy import String, Integer, Enum as SQLEnum, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, relationship, mapped_column
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
    
    # MODIFICATION : clerk_id est maintenant OBLIGATOIRE (nullable=False)
    clerk_id: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    
    # MODIFICATION : Suppression complète de hashed_password
    # hashed_password... (Supprimé)

    # On garde ce champ pour forcer le changement au premier login
    must_reset_password: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    email: Mapped[Optional[str]] = mapped_column(String, unique=True, index=True)
    first_name: Mapped[Optional[str]] = mapped_column(String)
    last_name: Mapped[Optional[str]] = mapped_column(String)
    image_url: Mapped[Optional[str]] = mapped_column(String)
    
    # Ces champs sont pour les bénéficiaires, nullable pour les agents/admins
    cin: Mapped[Optional[str]] = mapped_column(String, unique=True, index=True, nullable=True)
    rib: Mapped[Optional[str]] = mapped_column(String, unique=True, index=True, nullable=True)
    
    role: Mapped[UserRole] = mapped_column(SQLEnum(UserRole), nullable=False)
    
    bank_id: Mapped[Optional[int]] = mapped_column(ForeignKey("banks.id"), nullable=True)
    bank: Mapped[Optional["Bank"]] = relationship(back_populates="users")