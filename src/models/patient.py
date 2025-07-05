from datetime import datetime, date
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel
from uuid import UUID

class Gender(str, Enum):
    FEMALE = "female"
    MALE = "male"

class Patient(BaseModel):
    id: int
    uuid: UUID
    name_id: Optional[int] = None
    address_id: Optional[int] = None
    telecom_id: Optional[int] = None
    birth_date: date
    gender: Gender