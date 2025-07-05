from typing import Optional, Union, get_type_hints
from pydantic import BaseModel, model_validator
from uuid import UUID

class Address(BaseModel):
    patient_uuid: UUID
    line: list[str]
    city: str
    state: str
    postal_code: Optional[str] = None
    country: str

    class Config:
        extra = "forbid"  # Disallow extra fields not defined in the model

    @property
    def full_line_str(self) -> str:
        return ', '.join(self.line)

    @property
    def full_address(self) -> str:
        return f"{', '.join(self.line)}, {self.city}, {self.state}, {self.postalCode or ''}, {self.country}".strip(', ')
    
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