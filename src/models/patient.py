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
    name_id: int
    address_id: int
    telecom_id: int
    birth_date: date
    gender: Gender