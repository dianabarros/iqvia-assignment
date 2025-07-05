from typing import List, Tuple
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import tuple_

from models.raw_patient import RawPatient
from models.patient import Patient as PatientModel
from models.address import Address as AddressModel
from models.telecom import Telecom as TelecomModel
from models.patient_name import PatientName as PatientNameModel
from models.tables.patient_refined_tables import Patient, PatientName, Address, Telecom

class PatientProcessor:
    @staticmethod
    def process_patients(session: Session, patient_rows: List[RawPatient]) -> Tuple[bool, dict]:
        failed_patients = []
        failed_names = []
        failed_addresses = []
        failed_telecoms = []
        patient_objs = []
        patient_name_objs = []
        address_objs = []
        telecom_objs = []

        # Collect unique keys for deduplication
        patient_uuids = set()
        patient_name_keys = set()
        address_keys = set()
        telecom_keys = set()

        # Prepare objects to insert
        for patient_row in patient_rows:
            try:
                patient_uuid = UUID(patient_row.id)
            except Exception as e:
                failed_patients.append((patient_row.id, f"Invalid UUID: {e}"))
                continue

            # PatientName
            patient_names = []
            for name in patient_row.name:
                try:
                    key = (str(patient_uuid), name.use, name.family, tuple(name.given), tuple(name.prefix) if name.prefix else None)
                    if key in patient_name_keys:
                        continue
                    patient_name = PatientNameModel(
                        patient_uuid=patient_uuid,
                        use=name.use,
                        family=name.family,
                        given=name.given,
                        prefix=name.prefix if name.prefix else None
                    )
                    patient_names.append(patient_name)
                    patient_name_keys.add(key)
                except Exception as e:
                    failed_names.append((patient_row.id, str(e)))
            if not patient_names:
                failed_patients.append((patient_row.id, "No valid names found"))
                continue

            # Address
            patient_addresses = []
            for address in patient_row.address:
                try:
                    key = (
                        str(patient_uuid),
                        address.city,
                        address.state,
                        address.country,
                        getattr(address, "postalCode", None),
                        tuple(address.line),
                    )
                    if key in address_keys:
                        continue
                    patient_address = AddressModel(
                        patient_uuid=patient_uuid,
                        line=address.line,
                        city=address.city,
                        state=address.state,
                        postalCode=getattr(address, "postalCode", None),
                        country=address.country
                    )
                    patient_addresses.append(patient_address)
                    address_keys.add(key)
                except Exception as e:
                    failed_addresses.append((patient_row.id, str(e)))
            if not patient_addresses:
                failed_patients.append((patient_row.id, "No valid addresses found"))
                continue

            # Telecom
            patient_telecoms = []
            for telecom in patient_row.telecom:
                try:
                    key = (str(patient_uuid), telecom.system, telecom.value, telecom.use)
                    if key in telecom_keys:
                        continue
                    patient_telecom = TelecomModel(
                        patient_uuid=patient_uuid,
                        system=telecom.system,
                        value=telecom.value,
                        use=telecom.use
                    )
                    patient_telecoms.append(patient_telecom)
                    telecom_keys.add(key)
                except Exception as e:
                    failed_telecoms.append((patient_row.id, str(e)))
            if not patient_telecoms:
                failed_patients.append((patient_row.id, "No valid telecoms found"))
                continue

            # Patient
            try:
                patient_schema = PatientModel(
                    uuid=patient_uuid,
                    birth_date=patient_row.birthDate,
                    gender=patient_row.gender
                )
            except Exception as e:
                failed_patients.append((patient_row.id, str(e)))
                continue

            # Only add patient if there is at least one of each
            if patient_names and patient_addresses and patient_telecoms:
                patient_objs.append(patient_schema)
                patient_name_objs.extend(patient_names)
                address_objs.extend(patient_addresses)
                telecom_objs.extend(patient_telecoms)

        # Deduplicate before DB query
        patient_uuids = {p.uuid for p in patient_objs}
        patient_name_keys = {(n.patient_uuid, n.use, n.family, tuple(n.given), tuple(n.prefix) if n.prefix else None) for n in patient_name_objs}
        address_keys = {(a.patient_uuid, a.city, a.state, a.country, a.postalCode, tuple(a.line)) for a in address_objs}
        telecom_keys = {(t.patient_uuid, t.system, t.value, t.use) for t in telecom_objs}

        # Query existing records
        existing_patients = set(r[0] for r in session.query(Patient.uuid).filter(Patient.uuid.in_(patient_uuids)).all())
        existing_names = set(
            tuple(r) for r in session.query(
                PatientName.patient_uuid, PatientName.use, PatientName.family, PatientName.given, PatientName.prefix
            ).filter(
                tuple_(
                    PatientName.patient_uuid, PatientName.use, PatientName.family, PatientName.given, PatientName.prefix
                ).in_(list(patient_name_keys))
            ).all()
        )
        existing_addresses = set(
            tuple(r) for r in session.query(
                Address.patient_uuid, Address.city, Address.state, Address.country, Address.postalCode, Address.line
            ).filter(
                tuple_(
                    Address.patient_uuid, Address.city, Address.state, Address.country, Address.postalCode, Address.line
                ).in_(list(address_keys))
            ).all()
        )
        existing_telecoms = set(
            tuple(r) for r in session.query(
                Telecom.patient_uuid, Telecom.system, Telecom.value, Telecom.use
            ).filter(
                tuple_(
                    Telecom.patient_uuid, Telecom.system, Telecom.value, Telecom.use
                ).in_(list(telecom_keys))
            ).all()
        )

        # Filter out objects that already exist in DB
        patient_objs = [p for p in patient_objs if p.uuid not in existing_patients]
        patient_name_objs = [
            n for n in patient_name_objs
            if (n.patient_uuid, n.use, n.family, tuple(n.given), tuple(n.prefix) if n.prefix else None) not in existing_names
        ]
        address_objs = [
            a for a in address_objs
            if (a.patient_uuid, a.city, a.state, a.country, a.postalCode, tuple(a.line)) not in existing_addresses
        ]
        telecom_objs = [
            t for t in telecom_objs
            if (t.patient_uuid, t.system, t.value, t.use) not in existing_telecoms
        ]

        # Bulk insert
        if patient_objs:
            session.bulk_save_objects(patient_objs)
        if patient_name_objs:
            session.bulk_save_objects(patient_name_objs)
        if address_objs:
            session.bulk_save_objects(address_objs)
        if telecom_objs:
            session.bulk_save_objects(telecom_objs)
        # session.commit()
        success = len(failed_patients) == 0 and len(failed_names) == 0 and len(failed_addresses) == 0 and len(failed_telecoms) == 0
        return success, {
            "failed_patients": failed_patients,
            "failed_names": failed_names,
            "failed_addresses": failed_addresses,
            "failed_telecoms": failed_telecoms
        }