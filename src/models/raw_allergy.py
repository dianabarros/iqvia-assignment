from typing import List, Optional, Union
from pydantic import BaseModel

class Coding(BaseModel):
    system: str
    code: str
    display: str

class Code(BaseModel):
    coding: List[Union[None,Coding]]
    text: str

class PatientRef(BaseModel):
    reference: str

class RawAllergy(BaseModel):
    resourceType: str
    id: str
    type: str
    category: Optional[List[Union[str,None]]] = None
    criticality: str
    code: Code
    patient: PatientRef
    recordedDate: Optional[str] = None