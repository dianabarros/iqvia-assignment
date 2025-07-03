from datetime import datetime
from pydantic import BaseModel

from models.raw_patient import RawPatient

class RawPatientRow(BaseModel):
    id: int
    data: RawPatient
    ack: bool
    created_at: datetime
