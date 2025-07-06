import pytest
from sqlalchemy import create_engine, text

RAW_DB_URL = "postgresql+psycopg2://postgres:postgres@localhost:5432/raw_data"
REFINED_DB_URL = "postgresql+psycopg2://postgres:postgres@localhost:5433/refined_data"

@pytest.fixture(scope="module")
def raw_db_conn():
    engine = create_engine(RAW_DB_URL)
    with engine.connect() as conn:
        yield conn

@pytest.fixture(scope="module")
def refined_db_conn():
    engine = create_engine(REFINED_DB_URL)
    with engine.connect() as conn:
        yield conn

def test_patients_inserted_in_raw_db(raw_db_conn):
    result = raw_db_conn.execute(text("SELECT COUNT(*) FROM patients"))
    count = result.scalar()
    assert count > 0, "No patients found in raw_db after running reader"

def test_patients_transformed_in_refined_db(refined_db_conn):
    result = refined_db_conn.execute(text("SELECT COUNT(*) FROM patients"))
    count = result.scalar()
    assert count > 0, "No patients found in refined_db after running handler"