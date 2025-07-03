from typing import List, Optional, Union
from pydantic import BaseModel, model_validator

class Coding(BaseModel):
    system: str
    code: str
    display: str

class Code(BaseModel):
    coding: List[Coding]
    text: str

class PatientRef(BaseModel):
    reference: str

class RawAllergy(BaseModel):
    resourceType: str
    id: str
    type: str
    category: Optional[list] = None
    criticality: str
    code: Code
    patient: PatientRef
    recordedDate: Optional[str] = None

    @model_validator(mode="before")
    def empty_str_to_none(cls, values):
        # Only set to None if the field is Optional and the value is an empty string
        from typing import get_type_hints, Union
        hints = get_type_hints(cls)
        for k, v in values.items():
            if (
                isinstance(v, str) and v == "" and
                k in hints and (
                    getattr(hints[k], '__origin__', None) is Union and type(None) in hints[k].__args__
                )
            ):
                values[k] = None