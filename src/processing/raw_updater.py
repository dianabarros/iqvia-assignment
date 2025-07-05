
from typing import List
from sqlalchemy import update
from repository.database import SessionDatabase
from models.tables.raw_table import RawAllergies

class RawAllergyUpdater:
    @staticmethod
    def batch_ack_allergies(session: SessionDatabase, ids: List[str]) -> None:
        stmt = update(RawAllergies).where(
            RawAllergies.id.in_(ids)
        ).values(ack=True)
        session.execute(stmt)
