
import os
import json
import psycopg2
import psycopg2.extras
from datetime import datetime

from models.raw_patient_row import RawPatientRow
from models.raw_patient import RawPatient
from models.raw_allergy_row import RawAllergyRow
from models.raw_allergy import RawAllergy

from settings import settings

def process_and_store_data():
    raw_conn = None
    refined_conn = None
    raw_cur = None
    refined_cur = None
    try:
        # Connect to both databases
        raw_conn = psycopg2.connect(
            dbname=settings.RAW_DB_NAME,
            user=settings.RAW_DB_USER,
            password=settings.RAW_DB_PASSWORD,
            host=settings.RAW_DB_HOST,
            port=settings.RAW_DB_PORT
        )
        refined_conn = psycopg2.connect(
            dbname=settings.REFINED_DB_NAME,
            user=settings.REFINED_DB_USER,
            password=settings.REFINED_DB_PASSWORD,
            host=settings.REFINED_DB_HOST,
            port=settings.REFINED_DB_PORT
        )
        raw_cur = raw_conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        refined_cur = refined_conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        raw_conn.autocommit = False
        refined_conn.autocommit = False

        # # Ensure target tables exist
        # refined_cur.execute('''
        #     CREATE TABLE IF NOT EXISTS patients (
        #         id SERIAL PRIMARY KEY,
        #         data JSONB
        #     );
        # ''')
        # refined_cur.execute('''
        #     CREATE TABLE IF NOT EXISTS allergies (
        #         id SERIAL PRIMARY KEY,
        #         data JSONB
        #     );
        # ''')
        # refined_cur.execute('''
        #     CREATE TABLE IF NOT EXISTS metadata (
        #         id SERIAL PRIMARY KEY,
        #         timestamp TIMESTAMP,
        #         status TEXT
        #     );
        # ''')
        # refined_conn.commit()

        # Process patients
        raw_cur.execute('SELECT id, data, ack, created_at FROM patients WHERE ack = false;')
        patients = raw_cur.fetchall()
        if not patients:
            print("No new patient data to process.")
            # TODO
        batch_size = 1000  # TODO Define a batch size for processing
        for offset in range(0,len(patients), batch_size):
            patient_models_batch = []
            for row in patients[offset:offset + batch_size]:
                try:
                    raw_patient_row = RawPatientRow(
                        id=row['id'],
                        data=RawPatient(**row['data']),
                        ack=row['ack'],
                        created_at=row['created_at']
                    )
                    patient_models_batch.append(raw_patient_row)
                    print(f"Processing patient: {raw_patient_row.id}")
                except Exception as e:
                    print(f"Skipping malformed patient {row['id']} row: {e}")
                    continue
                # TODO: transform
                # TODO: insert into refined table
                # TODO: update ack status in raw table

            # Add any necessary transformations here
            # refined_cur.execute('INSERT INTO patients (data) VALUES (%s);', [json.dumps(patient)])

        # Process allergies
        raw_cur.execute('SELECT id, data, ack, created_at FROM allergies WHERE ack = false;')
        allergies = raw_cur.fetchall()
        if not allergies:
            print("No new allergy data to process.")
            # TODO
        batch_size = 1000  # TODO Define a batch size for processing
        for offset in range(0, len(allergies), batch_size):
            allergy_models_batch = []
            for row in allergies[offset:offset + batch_size]:
                try:
                    raw_allergy_row = RawAllergyRow(
                        id=row['id'],
                        data=RawAllergy(**row['data']),
                        ack=row['ack'],
                        created_at=row['created_at']
                    )
                    allergy_models_batch.append(raw_allergy_row)
                    print(f"Processing allergy: {raw_allergy_row.id}")
                except Exception as e:
                    print(f"Skipping malformed allergy {row['id']} row: {e}")
                    continue
                    # TODO: transform
                    # TODO: insert into refined table
                    # TODO: update ack status in raw table

            # Add any necessary transformations here
            # refined_cur.execute('INSERT INTO allergies (data) VALUES (%s);', [json.dumps(allergy)])

        # Record processing completion
        # refined_cur.execute('INSERT INTO metadata (timestamp, status) VALUES (%s, %s);', (datetime.now(), 'data_processed'))
        refined_conn.commit()
    except Exception as e:
        if refined_conn:
            refined_conn.rollback()
        print(f"Error occurred: {e}")
    finally:
        if raw_cur:
            raw_cur.close()
        if refined_cur:
            refined_cur.close()
        if raw_conn:
            raw_conn.close()
        if refined_conn:
            refined_conn.close()

if __name__ == '__main__':
    process_and_store_data()
