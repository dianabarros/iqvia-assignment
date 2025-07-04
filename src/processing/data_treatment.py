from typing import List
from datetime import datetime
from sqlalchemy import tuple_
from uuid import UUID

from models.raw_allergy import RawAllergy
from models.allergy_event import AllergyEventSchema
from models.allergy_code import AllergyCodeSchema
from models.tables.allergy_refined_tables import AllergyCodes, AllergyEvents
from repository.refined_db import get_refined_db_session

class AllergyProcessor:
    @staticmethod
    def process_allergies(allergy_rows: List[RawAllergy]) -> None:
        """
        Process a RawAllergy instance and return an AllergyRefinedTables instance.
        
        :param allergy_row: An instance of RawAllergy containing the raw allergy data.
        :return: An instance of AllergyRefinedTables with processed allergy data.
        """
        session = get_refined_db_session()
        code_keys = set()
        for allergy_row in allergy_rows:
            coding = AllergyCodeSchema(allergy_row.code.coding[0])
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
            session.commit()

        all_codes = session.query(AllergyCodes).filter(
            tuple_(AllergyCodes.code, AllergyCodes.system, AllergyCodes.display).in_(code_keys)
        ).all()
        code_map = {(c.code, c.system, c.display): c for c in all_codes}

        allergy_events = []
        for allergy_row in allergy_rows:
            coding = AllergyCodeSchema(allergy_row.code.coding[0])
            code_obj = code_map[(coding.code, coding.system, coding.display)]
            allergy_event_schema = AllergyEventSchema(
                id=UUID(allergy_row.id),
                patient_uuid=UUID(allergy_row.patient.reference),
                category=allergy_row.category,
                criticality=allergy_row.criticality,
                code_id=code_obj.id,
                recorded_date=allergy_row.recordedDate
            )
            allergy_event = AllergyEvents(
                **allergy_event_schema.model_dump(serialize=True),
                created_at=datetime.now()
            )
            allergy_events.append(allergy_event)

        session.bulk_save_objects(allergy_events)
        session.commit()