# backend/app/models/cheque.py

from sqlalchemy import String, Integer, Float, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from typing import Optional
import enum

from ..core.db import Base
from app.models.user import User
from app.models.bank import Bank


class Cheque(Base):
    __tablename__ = "cheques"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # Image du chèque (upload du bénéficiaire)
    image_url: Mapped[str] = mapped_column(String, nullable=False)

    # Date de dépôt (auto)
    date_depot: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Le bénéficiaire qui a déposé le chèque → user.role = BENEFICIAIRE
    beneficiaire_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    # Banque inscrite sur le chèque (choisie par le bénéficiaire)
    banque_cible_id: Mapped[int] = mapped_column(ForeignKey("banks.id"), nullable=False)

    