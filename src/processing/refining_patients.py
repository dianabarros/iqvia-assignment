from typing import List, Tuple
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import tuple_, and_, or_

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
                print(f"Skipping patient {patient_row.id} due to invalid UUID: {e}")
                failed_patients.append((patient_row.id, f"Invalid UUID: {e}"))
                continue

            # PatientName
            patient_names = []
            for name in patient_row.name:
                try:
                    patient_name = PatientNameModel(
                        patient_uuid=patient_uuid,
                        use=name.use,
                        family=name.family,
                        given=name.given,
                        prefix=name.prefix if name.prefix else None
                    )
                    patient_names.append(patient_name)
                    key = (str(patient_name.patient_uuid), patient_name.use, patient_name.family, patient_name.given, patient_name.prefix if patient_name.prefix else None)
                    patient_name_keys.add(key)
                except Exception as e:
                    print(f"Skipping name for patient {patient_row.id} due to error: {e}")
                    failed_names.append((patient_row.id, str(e)))
            if not patient_names:
                failed_patients.append((patient_row.id, "No valid names found"))
                continue

            # Address
            patient_addresses = []
            for address in patient_row.address:
                try:
                    patient_address = AddressModel(
                        patient_uuid=patient_uuid,
                        line=address.line,
                        city=address.city,
                        state=address.state,
                        postal_code=getattr(address, "postalCode", None),
                        country=address.country
                    )
                    patient_addresses.append(patient_address)
                    key = (
                        str(patient_address.patient_uuid),
                        patient_address.city,
                        patient_address.state,
                        patient_address.country,
                        patient_address.postal_code,
                        patient_address.full_line_str
                    )
                    address_keys.add(key)
                except Exception as e:
                    print(f"Skipping address for patient {patient_row.id} due to error: {e}")
                    failed_addresses.append((patient_row.id, str(e)))
            if not patient_addresses:
                failed_patients.append((patient_row.id, "No valid addresses found"))
                continue

            # Telecom
            patient_telecoms = []
            for telecom in patient_row.telecom:
                try:
                    patient_telecom = TelecomModel(
                        patient_uuid=patient_uuid,
                        system=telecom.system,
                        value=telecom.value,
                        use=telecom.use
                    )
                    patient_telecoms.append(patient_telecom)
                    key = (
                        str(patient_telecom.patient_uuid), 
                        patient_telecom.system, 
                        patient_telecom.value, 
                        patient_telecom.use
                    )
                    telecom_keys.add(key)
                except Exception as e:
                    print(f"Skipping telecom for patient {patient_row.id} due to error: {e}")
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
                print(f"Skipping patient {patient_row.id} due to schema incompatibility: {e}")
                failed_patients.append((patient_row.id, str(e)))
                continue

            # Only add patient if there is at least one of each
            if patient_names and patient_addresses and patient_telecoms:
                patient_objs.append(patient_schema)
                patient_name_objs.extend(patient_names)
                address_objs.extend(patient_addresses)
                telecom_objs.extend(patient_telecoms)
        

        # Query existing records
        existing_patients = set(r[0] for r in session.query(Patient.uuid).filter(Patient.uuid.in_(patient_uuids)).all())

        # PatientName deduplication
        existing_names = set()
        if patient_name_keys:
            name_filters = [
                and_(
                    PatientName.patient_uuid == k[0],
                    PatientName.use == k[1],
                    PatientName.family == k[2],
                    PatientName.given == k[3],
                    PatientName.prefix == k[4],
                ) for k in patient_name_keys
            ]
            existing_names = set(
                tuple(r) for r in session.query(
                    PatientName.patient_uuid, PatientName.use, PatientName.family, PatientName.given, PatientName.prefix
                ).filter(or_(*name_filters)).all()
            )

        # Address deduplication
        existing_addresses = set()
        if address_keys:
            address_filters = [
                and_(
                    Address.patient_uuid == k[0],
                    Address.city == k[1],
                    Address.state == k[2],
                    Address.country == k[3],
                    Address.postal_code == k[4],
                    Address.line == k[5],
                ) for k in address_keys
            ]
            existing_addresses = set(
                tuple(r) for r in session.query(
                    Address.patient_uuid, Address.city, Address.state, Address.country, Address.postal_code, Address.line
                ).filter(or_(*address_filters)).all()
            )

        # Telecom deduplication
        existing_telecoms = set()
        if telecom_keys:
            telecom_filters = [
                and_(
                    Telecom.patient_uuid == k[0],
                    Telecom.system == k[1],
                    Telecom.value == k[2],
                    Telecom.use == k[3],
                ) for k in telecom_keys
            ]
            existing_telecoms = set(
                tuple(r) for r in session.query(
                    Telecom.patient_uuid, Telecom.system, Telecom.value, Telecom.use
                ).filter(or_(*telecom_filters)).all()
            )

        # Filter out objects that already exist in DB
        patient_objs_to_insert = []
        for p in patient_objs:
            if p.uuid not in existing_patients:
                patient_objs_to_insert.append(Patient(
                        uuid=p.uuid,
                        birth_date=p.birth_date,
                        gender=p.gender
                    )
                )
        patient_name_objs_to_insert = []
        for n in patient_name_objs:
            if (n.patient_uuid, n.use, n.family, n.given, n.prefix if n.prefix else None) not in existing_names:
                patient_name_objs_to_insert.append(PatientName(
                        patient_uuid=n.patient_uuid,
                        use=n.use,
                        family=n.family,
                        given=n.given,
                        prefix=n.prefix if n.prefix else None
                    )
                )
        address_objs_to_insert = []
        for a in address_objs:
            if (a.patient_uuid, a.city, a.state, a.country, a.postal_code, a.full_line_str) not in existing_addresses:
                address_objs_to_insert.append(Address(
                        patient_uuid=a.patient_uuid,
                        line=a.full_line_str,
                        city=a.city,
                        state=a.state,
                        postal_code=a.postal_code,
                        country=a.country
                    )
                )
        telecom_objs_to_insert = []
        for t in telecom_objs:
            if (t.patient_uuid, t.system, t.value, t.use) not in existing_telecoms:
                telecom_objs_to_insert.append(Telecom(
                        patient_uuid=t.patient_uuid,
                        system=t.system,
                        value=t.value,
                        use=t.use
                    )
                )

        # Bulk insert
        if patient_objs_to_insert:
            session.bulk_save_objects(patient_objs_to_insert)
        if patient_name_objs_to_insert:
            session.bulk_save_objects(patient_name_objs_to_insert)
        if address_objs_to_insert:
            session.bulk_save_objects(address_objs_to_insert)
        if telecom_objs_to_insert:
            session.bulk_save_objects(telecom_objs_to_insert)
        success = len(failed_patients) == 0 and len(failed_names) == 0 and len(failed_addresses) == 0 and len(failed_telecoms) == 0
        return success, {
            "failed_patients": failed_patients,
            "failed_names": failed_names,
            "failed_addresses": failed_addresses,
            "failed_telecoms": failed_telecoms
        }