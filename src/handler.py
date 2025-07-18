
import os
import json
import psycopg2
import psycopg2.extras
from datetime import datetime

from models.raw_patient_row import RawPatientRow
from models.raw_patient import RawPatient
from models.raw_allergy_row import RawAllergyRow
from models.raw_allergy import RawAllergy
from processing.raw_updater import RawAllergyUpdater, RawPatientUpdater
from processing.refining_allergy import AllergyProcessor
from processing.refining_patients import PatientProcessor
from repository.database import get_sync_session_context
from repository.refined_db import sessionmaker as refined_sessionmaker
from repository.raw_db import sessionmaker as raw_sessionmaker

from settings import settings

def main():
    raw_db_sessionmaker = raw_sessionmaker
    refined_db_sessionmaker = refined_sessionmaker
    # Connect to database
    raw_conn = psycopg2.connect(
        dbname=settings.RAW_DB_NAME,
        user=settings.RAW_DB_USER,
        password=settings.RAW_DB_PASSWORD,
        host=settings.RAW_DB_HOST,
        port=settings.RAW_DB_PORT
    )
    raw_cur = raw_conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    raw_conn.autocommit = False

    raw_allergy_updater = RawAllergyUpdater()
    allergy_processor = AllergyProcessor()
    raw_patient_updater = RawPatientUpdater()
    patient_processor = PatientProcessor()

    # Process allergies
    raw_cur.execute('SELECT id, data, ack, created_at FROM allergies WHERE ack = false ORDER BY id ASC;')
    allergies = raw_cur.fetchall()
    if not allergies:
        print("No new allergy data to process.")
    batch_size = 1000  # TODO Define a batch size for processing
    for offset in range(0, len(allergies), batch_size):
        allergy_models_rows_batch = []
        allergy_models_batch = []
        for row in allergies[offset:offset + batch_size]:
            try:
                raw_allergy = RawAllergy(**row['data'])
                raw_allergy_row = RawAllergyRow(
                    id=row['id'],
                    data=raw_allergy,
                    ack=row['ack'],
                    created_at=row['created_at']
                )
                allergy_models_batch.append(raw_allergy)
                allergy_models_rows_batch.append(raw_allergy_row)
                print(f"Processing allergy: {raw_allergy_row.id}")
            except Exception as e:
                print(f"Skipping malformed allergy {row['id']} row: {e}")
                continue
        
        try:
            with get_sync_session_context(raw_db_sessionmaker, refined_db_sessionmaker) as (raw_db, refined_db):
                success, err = allergy_processor.process_allergies(refined_db,allergy_models_batch)
                ids_not_acked = []
                to_ack = []
                if not success:
                    print("Some data were malformed")
                    for malformed_coding in err['failed_allergy_coding_schema']:
                        ids_not_acked.append(malformed_coding[0])
                    for malformed_event in err['failed_allergy_event_schema']:
                        ids_not_acked.append(malformed_event[0])
                for row in allergy_models_rows_batch:
                    if row.data.id not in ids_not_acked:
                        to_ack.append(row.id)  
                raw_allergy_updater.batch_ack_allergies(raw_db, to_ack)
        except Exception as e:
            print(f"Batch processing failed from id {allergy_models_rows_batch[0].id} to id {allergy_models_rows_batch[len(allergy_models_rows_batch)-1].id}: {e}")
                 
    raw_cur.execute('SELECT id, data, ack, created_at FROM patients WHERE ack = false ORDER BY id ASC;')
    patients = raw_cur.fetchall()
    if not patients:
        print("No new patient data to process.")
    batch_size = 1000  # TODO Define a batch size for processing
    for offset in range(0, len(patients), batch_size):
        patient_models_rows_batch = []
        patient_models_batch = []
        for row in patients[offset:offset + batch_size]:
            try:
                raw_patient = RawPatient(**row['data'])
                raw_patient_row = RawPatientRow(
                    id=row['id'],
                    data=raw_patient,
                    ack=row['ack'],
                    created_at=row['created_at']
                )
                patient_models_rows_batch.append(raw_patient_row)
                patient_models_batch.append(raw_patient)
                print(f"Processing patient: {raw_patient_row.id}")
            except Exception as e:
                print(f"Skipping malformed patient {row['id']} row: {e}")
                continue

        try:
            with get_sync_session_context(raw_db_sessionmaker, refined_db_sessionmaker) as (raw_db, refined_db):
                success, err = patient_processor.process_patients(refined_db, patient_models_batch)
                ids_not_acked = []
                to_ack = []
                if not success:
                    print("Some data were malformed")
                    for malformed_patient in err['failed_patients']:
                        ids_not_acked.append(malformed_patient[0])
                    for malformed_name in err['failed_names']:
                        ids_not_acked.append(malformed_name[0])
                    for malformed_address in err['failed_addresses']:
                        ids_not_acked.append(malformed_address[0])
                    for malformed_telecom in err['failed_telecoms']:
                        ids_not_acked.append(malformed_telecom[0])
                for row in patient_models_rows_batch:
                    if row.data.id not in ids_not_acked:
                        to_ack.append(row.id)
                raw_patient_updater.batch_ack_patients(raw_db, to_ack)
        except Exception as e:
            print(f"Batch processing failed from id {patient_models_rows_batch[0].id} to id {patient_models_rows_batch[len(patient_models_rows_batch)-1].id}: {e}")
        raw_cur.close()
        raw_conn.close()
    

if __name__ == '__main__':
    main()
