from sqlalchemy import (
    Column, 
    String, 
    Integer, 
    Date, 
    ForeignKey, 
    UUID as SA_UUID
)
from sqlalchemy.orm import relationship
from models.tables import RefinedBase

class Patient(RefinedBase):
    __tablename__ = "patients"
    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(SA_UUID(as_uuid=True), unique=True, nullable=False)
    birth_date = Column(Date, nullable=False)
    gender = Column(String, nullable=False)
    names = relationship("PatientName", back_populates="patient", cascade="all, delete-orphan")
    addresses = relationship("Address", back_populates="patient", cascade="all, delete-orphan")
    telecoms = relationship("Telecom", back_populates="patient", cascade="all, delete-orphan")

class PatientName(RefinedBase):
    __tablename__ = "patient_names"
    id = Column(Integer, primary_key=True, autoincrement=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    use = Column(String, nullable=False)
    family = Column(String, nullable=False)
    given = Column(String, nullable=False)
    prefix = Column(String, nullable=True)
    patient = relationship("Patient", back_populates="names")

class Address(RefinedBase):
    __tablename__ = "addresses"
    id = Column(Integer, primary_key=True, autoincrement=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    line = Column(String, nullable=False)
    city = Column(String, nullable=False)
    state = Column(String, nullable=False)
    postal_code = Column(String, nullable=True)
    country = Column(String, nullable=False)
    patient = relationship("Patient", back_populates="addresses")

class Telecom(RefinedBase):
    __tablename__ = "telecoms"
    id = Column(Integer, primary_key=True, autoincrement=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    system = Column(String, nullable=False)
    value = Column(String, nullable=False)
    use = Column(String, nullable=False)
    patient = relationship("Patient", back_populates="telecoms")
