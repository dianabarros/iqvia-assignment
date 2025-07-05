from sqlalchemy import (
    Column, 
    Integer,
    Boolean, 
    DateTime
)
from sqlalchemy.dialects.postgresql import JSONB
from models.tables import RawBase

class RawPatients(RawBase):
    __tablename__ = "patients"
    id = Column(Integer, primary_key=True, autoincrement=True)
    data = Column(JSONB, nullable=False)
    ack = Column(Boolean, default=False)
    created_at = Column(DateTime, nullable=False)

class RawAllergies(RawBase):
    __tablename__ = "allergies"
    id = Column(Integer, primary_key=True, autoincrement=True)
    data = Column(JSONB, nullable=False)
    ack = Column(Boolean, default=False)
    created_at = Column(DateTime, nullable=False)