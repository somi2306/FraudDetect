# backend/app/models/details_cheque.py

from sqlalchemy import String, Integer, Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import date

from ..core.db import Base
# Utilisation de l'import relatif pour éviter les erreurs de cycle
from .cheque import Cheque 

class DetailsCheque(Base):
    __tablename__ = "details_cheque"

    id_detail: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    numero_cheque: Mapped[str] = mapped_column(String, nullable=False)
    montant_chiffre: Mapped[str] = mapped_column(String, nullable=False)
    montant_lettre: Mapped[str] = mapped_column(String, nullable=False)
    
    # CORRECTION 1 : Renommé en 'date_emission' pour correspondre au code et éviter le mot-clé SQL 'date'
    date_emission: Mapped[date] = mapped_column(Date, nullable=False)
    
    # CORRECTION 2 : Ajout des champs manquants (Lieu et Bénéficiaire)
    lieu: Mapped[str] = mapped_column(String, nullable=True)
    beneficiaire: Mapped[str] = mapped_column(String, nullable=True)
    
    numero_compte: Mapped[str] = mapped_column(String, nullable=False)
    signature: Mapped[str] = mapped_column(String, nullable=False)

    # Relation One-to-One
    cheque_id: Mapped[int] = mapped_column(ForeignKey("cheques.id"), nullable=False, unique=True)
    cheque = relationship("Cheque", backref="details_cheque")