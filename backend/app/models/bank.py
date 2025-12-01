# backend/app/models/bank.py

from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List
from ..core.db import Base 

class Bank(Base):
    __tablename__ = "banks"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    
    # Relation : Une banque peut avoir plusieurs utilisateurs (Agents)
    users: Mapped[List["User"]] = relationship(back_populates="bank")

    def __repr__(self) -> str:
        return f"Bank(id={self.id!r}, name={self.name!r})"