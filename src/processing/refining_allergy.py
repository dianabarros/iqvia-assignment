from typing import List, Tuple
from datetime import datetime
from sqlalchemy import tuple_
from uuid import UUID

from exceptions.exceptions import *
from models.raw_allergy import RawAllergy
from models.allergy_event import AllergyEventSchema
from models.allergy_code import AllergyCodeSchema
from models.tables.allergy_refined_tables import AllergyCodes, AllergyEvents
from repository.database import SessionDatabase


class AllergyProcessor:
    @staticmethod
    def process_allergies(session: SessionDatabase, allergy_rows: List[RawAllergy]) -> Tuple[bool, dict]:
        """
        Process a RawAllergy instance and return an AllergyRefinedTables instance.
        
        :param allergy_row: An instance of RawAllergy containing the raw allergy data.
        :return: An instance of AllergyRefinedTables with processed allergy data.
        """
        failed_allergy_code = []
        failed_allergy_event = []
        code_keys = set()
        for allergy_row in allergy_rows:
            try:
                coding = AllergyCodeSchema(**allergy_row.code.coding[0].model_dump())
            except Exception as e:
                print("Got an allergy coding schema incompatibility")
                failed_allergy_code.append((allergy_row.id, "Coding schema incompatibility: " + str(e)))
                continue
            code_keys.add((coding.code, coding.system, coding.display))

        
        existing_codes = session.query(AllergyCodes).filter(
            tuple_(AllergyCodes.code, AllergyCodes.system, AllergyCodes.display).in_(code_keys)
        ).all()
        code_map = {(c.code, c.system, c.display): c for c in existing_codes}

        missing_code_keys = [key for key in code_keys if key not in code_map]

        new_code_objs = [
            AllergyCodes(code=code, system=system, display=display)
            for code, system, display in missing_code_keys
        ]
        if new_code_objs:
            session.bulk_save_objects(new_code_objs)

        all_codes = session.query(AllergyCodes).filter(
            tuple_(AllergyCodes.code, AllergyCodes.system, AllergyCodes.display).in_(code_keys)
        ).all()
        code_map = {(c.code, c.system, c.display): c for c in all_codes}

        allergy_events = []
        for allergy_row in allergy_rows:
            coding_valid = True
            try:
                coding = AllergyCodeSchema(**allergy_row.code.coding[0].model_dump())
            except Exception as e:
                coding_valid = False
                print("Already caught before, no need to log again...")
            if coding_valid:
                code_obj = code_map[(coding.code, coding.system, coding.display)]
                try:
                    allergy_event_schema = AllergyEventSchema(
                        uuid=UUID(allergy_row.id),
                        patient_uuid=allergy_row.patient.reference,
                        category=allergy_row.category,
                        criticality=allergy_row.criticality,
                        code_id=code_obj.id,
                        recorded_date=allergy_row.recordedDate
                    )
                except Exception as e:
                    print(f"Got an allergy event schema incompatibility for uuid {allergy_row.id}")
                    print(e)
                    failed_allergy_event.append((allergy_row.id, "Allergy event schema incompatibility: " + str(e)))
                    continue
                allergy_event = AllergyEvents(
                    **allergy_event_schema.model_dump(),
                    created_at=datetime.now()
                )
                allergy_events.append(allergy_event)

        session.bulk_save_objects(allergy_events)
        
        all_data_success = len(failed_allergy_code) == 0 and len(failed_allergy_event) == 0
        return all_data_success, {
            "failed_allergy_coding_schema": failed_allergy_code,
            "failed_allergy_event_schema": failed_allergy_event
        }