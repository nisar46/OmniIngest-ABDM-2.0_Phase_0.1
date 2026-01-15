import pandas as pd
import random
from datetime import datetime, timedelta

def create_demo_data():
    # Scene 1 Data: The "Messy" Hospital File
    # We use a wrong header ('pt_name') to trigger Smart Mapping.
    
    data = []
    
    # 1. The Happy Path (Perfect Data)
    for i in range(10):
        data.append({
            'pt_name': f'Patient_{i}', 
            'abha_id': f'91-2026-{random.randint(1000,9999)}-{random.randint(1000,9999)}',
            'clinical_payload': '{"diagnosis": "Viral Fever", "visit": "OPD"}',
            'consent_status': 'GRANTED',
            'notice_id': f'N-2026-OK-{i}',
            'notice_date': '2026-01-10',
            'data_purpose': 'Treatment'
        })

    # 2. The "Quarantine" Trigger (Missing ABHA) - Scene 3
    data.append({
        'pt_name': 'Unknown_Trauma_Case',
        'abha_id': None, # MISSING!
        'clinical_payload': '{"condition": "Critical", "visit": "ER"}',
        'consent_status': 'DEEMED',
        'notice_id': 'N-2026-EMG-001',
        'notice_date': '2026-01-12',
        'data_purpose': 'Emergency'
    })
    
    # 3. The "Quarantine" Trigger (Malformed ID)
    data.append({
        'pt_name': 'Typo_Test_User',
        'abha_id': 'ABHA-BAD-FORMAT', # BAD FORMAT!
        'clinical_payload': '{"diagnosis": "Checkup"}',
        'consent_status': 'GRANTED',
        'notice_id': 'N-2026-CHK-002',
        'notice_date': '2026-01-11',
        'data_purpose': 'Care'
    })

    # 4. The "Purge" Trigger (Revoked Consent) - Scene 3
    data.append({
        'pt_name': 'Privacy_Advocate_User',
        'abha_id': '91-9999-8888-7777',
        'clinical_payload': '{"diagnosis": "Sensitive"}',
        'consent_status': 'REVOKED', # PURGE TRIGGER!
        'notice_id': 'N-2026-REV-001',
        'notice_date': '2026-01-01',
        'data_purpose': 'Treatment'
    })
    
    # 5. The "Purge" Trigger (Expired Notice)
    data.append({
        'pt_name': 'Old_Record_User',
        'abha_id': '91-1111-2222-3333',
        'clinical_payload': '{"diagnosis": "Flu"}',
        'consent_status': 'GRANTED',
        'notice_id': 'N-2024-EXP-001',
        'notice_date': '2024-05-20', # EXPIRED!
        'data_purpose': 'Research'
    })
    
    df = pd.DataFrame(data)
    
    # Save as EXCEL (.xlsx) to look "Enterprise"
    # Note: Requires openpyxl
    try:
        df.to_excel('demo_video_data.xlsx', index=False)
        print("SUCCESS: demo_video_data.xlsx created! Ready for Scene 1.")
        print(f"Total Rows: {len(df)}")
        print("Columns: ", df.columns.tolist())
    except ImportError:
        print("Error: openpyxl not installed. Saving as CSV fallback.")
        df.to_csv('demo_video_data.csv', index=False)

if __name__ == "__main__":
    create_demo_data()
