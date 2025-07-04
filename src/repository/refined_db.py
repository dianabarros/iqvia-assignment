from contextlib import contextmanager

from models.tables import RefinedBase
from repository.database import SessionDatabase, get_db_session

from settings import settings

sessionmaker = SessionDatabase(
    basemodel=RefinedBase,
    username=settings.REFINED_DB_USER,
    password=settings.REFINED_DB_PASSWORD,
    host=settings.REFINED_DB_HOST,
    database=settings.REFINED_DB_NAME
)

@contextmanager
def get_refined_db_session_context(commit_on_exception: bool = False):
    return get_db_session(sessionmaker, commit_on_exception)