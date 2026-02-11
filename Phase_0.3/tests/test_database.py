
import unittest
import os
import sqlite3
from src import database

class TestDatabase(unittest.TestCase):
    def setUp(self):
        # Use a test DB
        database.DB_NAME = "test_omnigest.db"
        database.init_db()

    def tearDown(self):
        if os.path.exists("test_omnigest.db"):
            os.remove("test_omnigest.db")

    def test_save_and_retrieve(self):
        dummy_data = {
            "Notice_ID": "N-TEST-001",
            "ABHA_ID": "91-0000-0000-0000",
            "Patient_Name": "Test Patient",
            "Notice_Date": "2026-01-01",
            "Consent_Status": "GRANTED",
            "Clinical_Payload": "Test Data",
            "Ingest_Status": "PROCESSED"
        }
        database.save_record(dummy_data)
        
        df = database.get_all_records()
        self.assertFalse(df.is_empty())
        self.assertEqual(df['notice_id'][0], "N-TEST-001")

    def test_hard_delete(self):
        dummy_data = {"Notice_ID": "N-TEST-002", "Patient_Name": "Delete Me"}
        database.save_record(dummy_data)
        
        database.hard_delete_all()
        df = database.get_all_records()
        self.assertTrue(df.is_empty())

if __name__ == '__main__':
    unittest.main()
