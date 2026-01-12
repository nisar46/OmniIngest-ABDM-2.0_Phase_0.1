import pandas as pd

def create_demo_data():
    # Specific records to showcase features
    data = [
        {
            'pt_name': 'Vikram Malhotra', # WRONG HEADER: should be patient_name
            'abha-number': '91-1234-5678-9012', # WRONG HEADER: should be abha_id
            'clinical_payload': '{"diagnosis": "Hyper-tension", "visit": "OPD"}',
            'consent_status': 'ACTIVE',
            'notice_id': 'N-2026-CONS-v1.2',
            'notice_date': '2026-01-10',
            'data_purpose': 'Treatment'
        },
        {
            'patient_name': 'Priya Lakshmi',
            'abha_id': None, # MISSING ABHA: triggers Compliance "Yell"
            'clinical_payload': '{"diagnosis": "Diabetes Type 2", "visit": "IPD"}',
            'consent_status': 'PENDING',
            'notice_id': 'N-2026-CONS-v1.1',
            'notice_date': '2025-12-15',
            'data_purpose': 'Consultation'
        },
        {
            'patient_name': 'Anil Sharma',
            'abha_id': 'ABHA-777', # MALFORMED ABHA: triggers Quality Check
            'clinical_payload': '{"diagnosis": "Annual Checkup"}',
            'consent_status': 'REVOKED',
            'notice_id': 'N-2025-CONS-v0.9', # OUTDATED NOTICE: 2025 check
            'notice_date': '2025-05-20',
            'data_purpose': 'Audit'
        }
    ]
    
    df = pd.DataFrame(data)
    # Save as CSV
    df.to_csv('demo_video_data.csv', index=False)
    print("SUCCESS: demo_video_data.csv created for your LinkedIn video!")

if __name__ == "__main__":
    create_demo_data()
