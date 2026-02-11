
import sqlite3
import json
import os
from datetime import datetime

DB_NAME = "omnigest.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # Patients Table (The "Filing Cabinet")
    c.execute('''CREATE TABLE IF NOT EXISTS patients (
        notice_id TEXT PRIMARY KEY,
        abha_id TEXT,
        patient_name TEXT,
        notice_date TEXT,
        consent_status TEXT,
        clinical_payload TEXT,
        ingest_status TEXT,
        status_reason TEXT,
        ingest_timestmp TEXT
    )''')
    
    # [Migration] Attempt to add column if it doesn't exist (for existing DBs)
    try:
        c.execute("ALTER TABLE patients ADD COLUMN status_reason TEXT")
    except:
        pass # Column likely exists
    
    # Audit Table (Immutable Log)
    c.execute('''CREATE TABLE IF NOT EXISTS audit_log (
        log_id TEXT PRIMARY KEY,
        timestamp TEXT,
        action TEXT,
        details TEXT
    )''')
    
    conn.commit()
    conn.close()

def save_record(data: dict):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    try:
        c.execute('''INSERT OR REPLACE INTO patients 
                  (notice_id, abha_id, patient_name, notice_date, consent_status, clinical_payload, ingest_status, status_reason, ingest_timestmp)
                  VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                  (data.get('Notice_ID'), data.get('ABHA_ID'), data.get('Patient_Name'), 
                   data.get('Notice_Date'), data.get('Consent_Status'), data.get('Clinical_Payload'),
                   data.get('Ingest_Status', 'PROCESSED'), data.get('Status_Reason', 'N/A'), datetime.now().isoformat()))
        conn.commit()
    except Exception as e:
        print(f"DB Error: {e}")
    finally:
        conn.close()

def get_all_records():
    conn = sqlite3.connect(DB_NAME)
    import polars as pl
    try:
        # Use pandas for easy sql read then to polars
        import pandas as pd
        df = pd.read_sql("SELECT * FROM patients", conn)
        
        # [Fix] Remap lowercase DB columns back to Canonical Schema for App compatibility
        rename_map = {
            "notice_id": "Notice_ID",
            "abha_id": "ABHA_ID",
            "patient_name": "Patient_Name",
            "notice_date": "Notice_Date",
            "consent_status": "Consent_Status",
            "clinical_payload": "Clinical_Payload",
            "ingest_status": "Ingest_Status",
            "status_reason": "Status_Reason"
        }
        df = df.rename(columns=rename_map)
        
        return pl.from_pandas(df)
    except Exception as e:
        return pl.DataFrame()
    finally:
        conn.close()

def hard_delete_all():
    """Rule 8.3: Targeted True SQL Delete for Revoked/Expired Records only."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # ONLY delete the records marked for Purge (Red), keep the Green/Orange ones.
    c.execute("DELETE FROM patients WHERE ingest_status = 'PURGED'")
    conn.commit()
    conn.close()
