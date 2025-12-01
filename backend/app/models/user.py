# backend/app/models/user.py
from sqlalchemy import String, Integer, Enum as SQLEnum
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from typing import Optional
from enum import Enum
from ..core.db import Base 

class UserRole(str, Enum):
    ADMIN = "Admin"
    AGENT = "Agent"
    BENEFICIAIRE = "Bénéficiaire"

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    clerk_id: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String, unique=True, index=True)
    first_name: Mapped[Optional[str]] = mapped_column(String)
    last_name: Mapped[Optional[str]] = mapped_column(String)
    image_url: Mapped[Optional[str]] = mapped_column(String)
    cin: Mapped[Optional[str]] = mapped_column(String, unique=True, index=True)
    rib: Mapped[Optional[str]] = mapped_column(String, unique=True, index=True)
    role: Mapped[UserRole] = mapped_column(SQLEnum(UserRole), nullable=False)