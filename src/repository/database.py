from contextlib import contextmanager
from typing import Generator, Tuple

from sqlalchemy import URL, create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

BaseModel = declarative_base()

class SessionDatabase:
    def __init__(self, basemodel, username, password, host, database) -> None:
        url_object = URL.create(
            "postgresql+psycopg2",
            username=username,
            password=password,
            host=host,
            database=database,
        )

        self.engine = create_engine(url_object)
        basemodel.metadata.create_all(self.engine)
        self.session = sessionmaker(bind=self.engine)
        print("Database connection opened")

def get_db_session(
    sessionmanager: SessionDatabase,
    commit_on_exception: bool = False
) -> Generator[tuple[Session, Session], None, None]:
    db = sessionmanager.session()
    try:
        yield db
        db.commit()
    except Exception as e:
        if commit_on_exception:
            db.commit()
        else:
            db.rollback()
        print(f"Closing database session due to error: {str(e)}")
        raise e
    finally:
        db.close()


def sync_dbs_session(
    raw_sessionmanager: SessionDatabase,
    refined_sessionmanager: SessionDatabase,
) -> Generator[Tuple[Session, Session], None, None]:
    """
    Context manager generator to synchronize operations between two database sessions.

    Parameters:
        raw_sessionmanager (SessionDatabase): The session manager for the raw database.
        refined_sessionmanager (SessionDatabase): The session manager for the refined database.

    Yields:
        Tuple[Session, Session]: A tuple containing the raw and refined SQLAlchemy Session objects.

    This function ensures that both sessions are committed if no exception occurs,
    or rolled back if an exception is raised. Both sessions are properly closed after use.
    """
    raw_db = raw_sessionmanager.session()
    refined_db = refined_sessionmanager.session()
    try:
        yield raw_db, refined_db
        raw_db.commit()
        refined_db.commit()
    except Exception as e:
        raw_db.rollback()
        refined_db.rollback()
        print(f"Closing database session due error: {str(e)}")
        raise e
    finally:
        raw_db.close()
        refined_db.close()
        print(f"Database sessions closed")

@contextmanager
def get_sync_session_context(
    raw_db: SessionDatabase, 
    refined_db: SessionDatabase
) -> Generator[Tuple[Session, Session], None, None]:
    return sync_dbs_session(raw_db, refined_db)
