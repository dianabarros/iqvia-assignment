from datetime import datetime
from pydantic import BaseModel, field_validator
from typing import Optional
from uuid import UUID
from enum import Enum

class AllergyCategory(str, Enum):
    FOOD = "food"
    PET_ALLERGY = "pet_allergy"
    ENVIRONMENT = "environment"

class AllergyEvent(BaseModel):
    uuid: UUID
    patient_uuid: UUID
    category: Optional[AllergyCategory] = None
    criticality: str
    code_id: int
    recorded_date: datetime

    class Config:
        extra = "forbid"

    @field_validator('category', mode='before')
    @classmethod
    def validate_category(cls, v, info):
        if isinstance(v, list):
            if len(v) == 0:
                return None
            if len(v) == 1 and isinstance(v[0], str):
                if v[0] == "" or v[0] is None:
                    return None
                v = v[0].lower().strip()
                if v == "environmental":
                    return AllergyCategory.ENVIRONMENT
        return v
    
    @field_validator('patient_uuid', mode='before')
    @classmethod
    def validate_patient_uuid(cls, v):
        if isinstance(v, str):
            uuid = v.lower().strip().replace("patient/", "")
            return UUID(uuid)
        return v
    
    @field_validator('recorded_date', mode='before')
    @classmethod
    def validate_recorded_date(cls, v):
        if isinstance(v, str):
            try:
                return datetime.fromisoformat(v)
            except ValueError:
                raise ValueError(f"Invalid date format: {v}")
        return v
    
    @field_validator('criticality', mode='before')
    @classmethod
    def validate_criticality(cls, v):
        if v == "":
            raise ValueError("Criticality cannot be an empty string.")
        return v
            