from typing import Generator

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
) -> Generator[Session, None, None]:
    db = sessionmanager.session()
    try:
        yield db
        db.commit()
    except Exception as e:
        if commit_on_exception:
            db.commit()
        else:
            db.rollback()
        print(f"Closing database session due error: {str(e)}")
        raise e
    finally:
        db.close()

