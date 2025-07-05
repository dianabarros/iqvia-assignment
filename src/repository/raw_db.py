from contextlib import contextmanager
from models.tables import RawBase
from repository.database import SessionDatabase, get_db_session

from settings import settings

sessionmaker = SessionDatabase(
    basemodel=RawBase,
    username=settings.RAW_DB_USER,
    password=settings.RAW_DB_PASSWORD,
    host=settings.RAW_DB_HOST,
    database=settings.RAW_DB_NAME
)

@contextmanager
def get_raw_db_session_context(commit_on_exception: bool = False):
    return get_db_session(sessionmaker, commit_on_exception)