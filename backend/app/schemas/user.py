# backend/app/schemas/user.py
import pydantic
from typing import Optional
from enum import Enum

class UserRole(str, Enum):
    ADMIN = "Admin"
    AGENT = "Agent"
    BENEFICIAIRE = "Bénéficiaire"

class UserSync(pydantic.BaseModel):
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    imageUrl: Optional[str] = None
    email: Optional[str] = None
    cin: Optional[str] = None
    rib: Optional[str] = None
    bank_code: Optional[str] = None  # Code de banque (230, 007, 145)