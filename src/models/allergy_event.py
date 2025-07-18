from datetime import datetime
from pydantic import BaseModel, field_validator
from typing import Optional
from uuid import UUID
from enum import Enum

class AllergyCategory(str, Enum):
    FOOD = "food"
    PET_ALLERGY = "pet_allergy"
    ENVIRONMENT = "environment"


class AllergyEventSchema(BaseModel):
    uuid: UUID
    patient_uuid: UUID
    category: Optional[AllergyCategory] = None
    criticality: str
    code_id: Optional[int] = None
    recorded_date: datetime

    class Config:
        extra = "forbid"

    @field_validator('category', mode='before')
    @classmethod
    def validate_category(cls, v, info):
        category_mapping = {
            "food": AllergyCategory.FOOD,
            "pet_allergy": AllergyCategory.PET_ALLERGY,
            "pet allergies": AllergyCategory.PET_ALLERGY,
            "environment": AllergyCategory.ENVIRONMENT,
            "environmental": AllergyCategory.ENVIRONMENT
        }
        if isinstance(v, list):
            if len(v) == 0:
                return None
            if len(v) == 1:
                if isinstance(v[0], str):
                    if v[0] == "":
                        return None
                    v = v[0].lower().strip()
                    return category_mapping.get(v)
                if v[0] is None:
                    return None
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
        elif isinstance(v, datetime):
            return v
        raise ValueError(f"Invalid date type: {type(v)}. Expected str or datetime.")
    
    @field_validator('criticality', mode='before')
    @classmethod
    def validate_criticality(cls, v):
        if v == "":
            raise ValueError("Criticality cannot be an empty string.")
        return v
            