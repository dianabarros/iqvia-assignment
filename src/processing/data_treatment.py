from datetime import datetime
from uuid import UUID,uuid

from models.raw_allergy import RawAllergy
from models.allergy_event import AllergyEventSchema
from models.allergy_code import AllergyCodeSchema
from models.allergy_refined_tables import AllergyCodes, AllergyEvents
from repository.refined_db import get_refined_db_session

class AllergyProcessor:
    @staticmethod
    def process_allergies(allergy_row: RawAllergy) -> AllergyRefinedTables:
        """
        Process a RawAllergy instance and return an AllergyRefinedTables instance.
        
        :param allergy_row: An instance of RawAllergy containing the raw allergy data.
        :return: An instance of AllergyRefinedTables with processed allergy data.
        """
        session = get_refined_db_session()
        coding = AllergyCodeSchema(allergy_row.code.coding[0])
        code_obj = session.query(AllergyCodes).filter_by(
            code=coding.code,
            system=coding.system,
            display=coding.display
        ).first()
        code_id = code_obj.id if code_obj else None
        if not code_obj:
            code_obj = AllergyCodes(
                code=coding.code,
                system=coding.system,
                display=coding.display
            )
            session.add(code_obj)
            session.commit()
            session.refresh(code_obj)

        if code_id is None:
            inserted_code_obj = session.query(AllergyCodes).filter_by(
                code=coding.code,
                system=coding.system,
                display=coding.display
            ).first()
            code_id = inserted_code_obj.id
        allergy_event_schema = AllergyEventSchema(
            id=UUID(allergy_row.id),
            patient_uuid=UUID(allergy_row.patient.reference),
            category=allergy_row.category,
            criticality=allergy_row.criticality,
            code_id=code_id,
            recorded_date=allergy_row.recordedDate
        )
        allergy_event = AllergyEvents(
            **allergy_event_schema.model_dump(serialize=True),
            created_at=datetime.now()
        )
        session.add(allergy_event)
        session.commit()
        session.refresh(allergy_event)


        