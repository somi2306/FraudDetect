from pydantic import BaseModel
from typing import Optional
from uuid import UUID
import datetime

class CheckBase(BaseModel):
    amount: float
    bank_name: str
    check_number: str
    beneficiary_id: UUID
    check_image_url: Optional[str] = None

class CheckCreate(CheckBase):
    pass

class Check(CheckBase):
    id: UUID
    created_at: datetime.datetime
    status: str

    class Config:
        orm_mode = True
