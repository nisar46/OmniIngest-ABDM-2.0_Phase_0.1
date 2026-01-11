import sqlite3
import json
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_path="omningest.db"):
        self.db_path = db_path
        self.init_db()

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def init_db(self):
        """Initializes the database schema."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS patients (
                    abha_id TEXT PRIMARY KEY,
                    patient_name TEXT,
                    consent_status TEXT,
                    notice_date TEXT,
                    discovery_status TEXT,
                    clinical_summary TEXT,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS access_logs (
                    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    abha_id TEXT,
                    action TEXT,
                    purpose TEXT,
                    user_id TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()

    def log_access(self, abha_id, action, purpose, user_id="SYSTEM"):
        """Logs a data access event for DPDP compliance."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO access_logs (abha_id, action, purpose, user_id, timestamp)
                VALUES (?, ?, ?, ?, ?)
            ''', (abha_id, action, purpose, user_id, datetime.now().isoformat()))
            conn.commit()

    def upsert_patient(self, abha_id, name, status, notice_date, discovery="", clinical=""):
        """Inserts or updates a patient record."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO patients (abha_id, patient_name, consent_status, notice_date, discovery_status, clinical_summary, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(abha_id) DO UPDATE SET
                    patient_name=excluded.patient_name,
                    consent_status=excluded.consent_status,
                    notice_date=excluded.notice_date,
                    discovery_status=excluded.discovery_status,
                    clinical_summary=excluded.clinical_summary,
                    last_updated=excluded.last_updated
            ''', (abha_id, name, status, notice_date, discovery, clinical, datetime.now().isoformat()))
            conn.commit()

    def get_patient(self, abha_id):
        """Retrieves a patient record by ABHA_ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM patients WHERE abha_id = ?', (abha_id,))
            row = cursor.fetchone()
            if row:
                return {
                    "abha_id": row[0],
                    "name": row[1],
                    "status": row[2],
                    "notice_date": row[3],
                    "discovery": row[4],
                    "clinical": row[5]
                }
            return None

    def get_all_patients(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM patients')
            return cursor.fetchall()

if __name__ == "__main__":
    db = DatabaseManager()
    db.upsert_patient("ABHA007", "James Bond", "ACTIVE", "2025-01-01", "MANUAL", "Consultation")
    print(f"Stored Patients: {db.get_all_patients()}")
