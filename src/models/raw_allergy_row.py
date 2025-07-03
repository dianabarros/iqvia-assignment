from datetime import datetime
from pydantic import BaseModel

from models.raw_allergy import RawAllergy

class RawAllergyRow(BaseModel):
    id: int
    data: RawAllergy
    ack: bool
    created_at: datetime
