from typing import List, Optional
from pydantic import BaseModel, model_validator

class Name(BaseModel):
    use: str
    family: str
    given: List[str]
    prefix: Optional[List[str]] = None

class Telecom(BaseModel):
    system: str
    value: str
    use: str

class Address(BaseModel):
    line: List[str]
    city: str
    state: str
    postalCode: Optional[str] = None
    country: str

class RawPatient(BaseModel):
    resourceType: str
    id: str 
    name: List[Name]
    telecom: List[Telecom]
    gender: str
    birthDate: str
    address: List[Address]