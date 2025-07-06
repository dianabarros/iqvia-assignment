from datetime import datetime, date
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel
from uuid import UUID

class Gender(str, Enum):
    FEMALE = "female"
    MALE = "male"

class Patient(BaseModel):
    uuid: UUID
    birth_date: date
    gender: Gender