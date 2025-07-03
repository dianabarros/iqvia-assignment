from typing import Optional, Union, get_type_hints
from pydantic import BaseModel, model_validator

class AllergySystem(BaseModel):
    id: int
    system_name: str
    code: str
    display: str

    class Config:
        extra = "forbid"
    
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