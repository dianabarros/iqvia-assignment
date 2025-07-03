from typing import Optional, Union, get_type_hints
from pydantic import BaseModel, model_validator, field_validator
from uuid import UUID

class PatientName(BaseModel):
    id: int
    patient_uuid: UUID
    use: str
    family: str
    given: str
    prefix: Optional[str] = None

    @model_validator(mode="before")
    def empty_str_to_none(cls, values):
        hints = get_type_hints(cls)
        for k, v in values.items():
            # Only set to None if the field is Optional and the value is an empty string
            if isinstance(v, str) and v == "":
                if (k in hints and (
                        getattr(hints[k], '__origin__', None) is Union and type(None) in hints[k].__args__
                    )
                ):
                    values[k] = None
                else:
                    raise ValueError(f"Field '{k}' cannot be an empty string.")
        return values
    
    @field_validator('family', 'given', 'prefix', mode='before')
    @classmethod
    def list_to_str(cls, v, info):
        if isinstance(v, list):
            if len(v) == 1 and isinstance(v[0], str):
                if v[0] == "" and not cls.model_fields[info.field_name].required:
                    return None
                return v[0]
            else:
                raise ValueError(f"Field must be a single string, got {v}")
        return v

    class Config:
        extra = "forbid"  # Disallow extra fields not defined in the model