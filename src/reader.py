import json
import ndjson
import psycopg2
import psycopg2.extras
import os
from datetime import datetime

from settings import settings

def read_and_store_data():
    # Connect to PostgreSQL for data history
    conn = None
    cur = None
    try:
        conn = psycopg2.connect(
            dbname=settings.RAW_DB_NAME,
            user=settings.RAW_DB_USER,
            password=settings.RAW_DB_PASSWORD,
            host=settings.RAW_DB_HOST,
            port=settings.RAW_DB_PORT
        )
        cur = conn.cursor()
        # Start transaction
        conn.autocommit = False

        # Create tables if not exist
        cur.execute('''
            CREATE TABLE IF NOT EXISTS patients (
                id SERIAL PRIMARY KEY,
                data JSONB,
                ack BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP
            );
        ''')
        print("Patients table created or already exists.")
        cur.execute('''
            CREATE TABLE IF NOT EXISTS allergies (
                id SERIAL PRIMARY KEY,
                data JSONB,
                ack BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP
            );
        ''')
        print("Allergies table created or already exists.")

        # Read Patient data
        with open('/data/Patient.ndjson', 'r') as f:
            for i, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    patient = json.loads(line)
                    cur.execute('INSERT INTO patients (data, created_at) VALUES (%s,%s);', [psycopg2.extras.Json(patient), datetime.now()])
                except Exception as e:
                    print(f"Skipping malformed patient line {i}: {e}")

        # Read Allergy data
        with open('/data/AllergyIntolerance.ndjson', 'r') as f:
            for i, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    allergy = json.loads(line)
                    cur.execute('INSERT INTO allergies (data, created_at) VALUES (%s,%s);', [psycopg2.extras.Json(allergy), datetime.now()])
                except Exception as e:
                    print(f"Skipping malformed allergy line {i}: {e}")

        conn.commit()
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Error occurred: {e}")
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

if __name__ == '__main__':
    read_and_store_data()
    print("Finished")
