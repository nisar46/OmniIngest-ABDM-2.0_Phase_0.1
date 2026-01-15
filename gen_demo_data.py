import pandas as pd
import random
from datetime import datetime

def generate_demo_data():
    # 1 Revoked, 2 Active records
    data = [
        # Revoked Record
        {
            "Patient_Name": "Vikram Malhotra",
            "ABHA_ID": "91-8888-7777",
            "Notice_ID": f"N-{datetime.now().strftime('%Y%m%d')}001",
            "Notice_Date": datetime.now().strftime("%Y-%m-%d"),
            "Consent_Status": "REVOKED",
            "Mobile": "+91-9876543210",
            "DOB": "1985-05-12",
            "Address": "12, Block A, Dwarka, Delhi",
            "Clinical_Payload": "{'diagnosis': 'Hypertension', 'medication': 'Amlodipine 5mg'}"
        },
        # Active Record 1
        {
            "Patient_Name": "Priya Sharma",
            "ABHA_ID": "91-1234-5678",
            "Notice_ID": f"N-{datetime.now().strftime('%Y%m%d')}002",
            "Notice_Date": datetime.now().strftime("%Y-%m-%d"),
            "Consent_Status": "GRANTED",
            "Mobile": "+91-9988776655",
            "DOB": "1992-08-22",
            "Address": "45, Street 7, Indiranagar, Bangalore",
            "Clinical_Payload": "{'diagnosis': 'Type 2 Diabetes', 'medication': 'Metformin 500mg'}"
        },
        # Active Record 2
        {
            "Patient_Name": "Rahul Singh",
            "ABHA_ID": "91-5555-4444",
            "Notice_ID": f"N-{datetime.now().strftime('%Y%m%d')}003",
            "Notice_Date": datetime.now().strftime("%Y-%m-%d"),
            "Consent_Status": "GRANTED",
            "Mobile": "+91-7777766666",
            "DOB": "1978-11-30",
            "Address": "Flat 303, Bandra West, Mumbai",
            "Clinical_Payload": "{'diagnosis': 'Seasonal Allergies', 'medication': 'Cetirizine 10mg'}"
        }
    ]
    
    df = pd.DataFrame(data)
    df.to_csv("demo_sample.csv", index=False)
    print("Generated demo_sample.csv with 1 Revoked and 2 Active records.")

if __name__ == "__main__":
    generate_demo_data()
