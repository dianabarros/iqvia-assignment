from typing import Optional
from pydantic import BaseModel
from uuid import UUID

class Telecom(BaseModel):
    patient_uuid: UUID
    system: str
    value: str
    use: str

    class Config:
        extra = "forbid"

    @property
    def is_email(self) -> bool:
        return self.system == "email"

    @property
    def is_phone(self) -> bool:
        return self.system == "phone" or self.system == "mobile"