from sqlalchemy import (
    Column, 
    UUID, 
    String, 
    Integer, 
    ForeignKey,
    DateTime
)
from sqlalchemy.orm import relationship
from models.tables import RefinedBase

class AllergyCodes(RefinedBase):
    __tablename__ = "allergy_codes"
    id = Column(Integer, primary_key=True, autoincrement=True)
    system = Column(String, nullable=False)
    code = Column(String, nullable=False)
    display = Column(String, nullable=False)
    events = relationship("AllergyEvents", back_populates="code_rel")

class AllergyEvents(RefinedBase):
    __tablename__ = "allergy_events"
    uuid = Column(UUID(as_uuid=True), primary_key=True)
    patient_uuid = Column(UUID(as_uuid=True), nullable=False)
    category = Column(String, nullable=True)
    criticality = Column(String, nullable=False)
    code_id = Column(Integer, ForeignKey("allergy_codes.id"), nullable=False)
    recorded_date = Column(DateTime, nullable=False)
    created_at = Column(DateTime, nullable=False)
    code_rel = relationship("AllergyCodes", back_populates="events")

        