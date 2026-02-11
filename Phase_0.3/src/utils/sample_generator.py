"""
Script to create sample raw data files in all supported formats
"""

import pandas as pd
import json
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import random

def main(num_rows=1000):
    # Generate sample data
    # num_rows passed from argument
    sample_data = []

    for i in range(num_rows):
        # Use random suffixes to ensure files change appropriately
        rand_suffix = random.randint(1000, 9999)
        
        # Scenario Logic
        # 1. ABHA_ID Generation (Compliant vs Malformed vs Missing)
        rand_val = random.random()
        if rand_val < 0.05:
            abha_id = None # Missing (Quarantine)
        elif rand_val < 0.10:
            abha_id = f"ABHA-{random.randint(100, 999)}" # Malformed (Quarantine)
        else:
            # Compliant format: XX-XXXX-XXXX-XXXX
            abha_id = f"{random.randint(10, 99)}-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}"
            
        # 2. Randomly use 2025 Notice IDs for Outdated Error (5% chance)
        year = 2026
        if random.random() < 0.05:
            year = 2025
        notice_id = f"N-{year}-CONS-v1.{random.randint(0,9)}"
        
        sample_data.append({
            'patient_name': f'Patient_{i+1}_{rand_suffix}',
            'abha_id': abha_id,
            'clinical_payload': f'{{"diagnosis": "{random.choice(["Condition", "Issue", "Case"])}_{i+1}", "treatment": "Treatment_{i+1}", "visit_type": "{random.choice(["OPD", "IPD", "EMERGENCY"])}"}}',
            'consent_status': random.choice(['ACTIVE', 'PENDING', 'GRANTED', 'REVOKED']),
            'notice_id': notice_id,
            'notice_date': (datetime.now() - timedelta(days=random.randint(0, 450))).strftime('%Y-%m-%d'),
            'data_purpose': random.choice(["Consultation", "Treatment", "Audit", "Emergency Care", "Marketing"])
        })

    print("Creating sample data files in all formats...")

    # 1. CSV
    print("Creating CSV file...")
    df = pd.DataFrame(sample_data)
    df.to_csv('raw_data.csv', index=False)
    print("[OK] Created raw_data.csv")

    # 2. JSON
    print("Creating JSON file...")
    with open('raw_data.json', 'w', encoding='utf-8') as f:
        json.dump(sample_data, f, indent=2)
    print("[OK] Created raw_data.json")

    # 3. XML
    print("Creating XML file...")
    root = ET.Element('patients')
    for record in sample_data:
        patient = ET.SubElement(root, 'patient')
        for key, value in record.items():
            elem = ET.SubElement(patient, key)
            elem.text = str(value)

    tree = ET.ElementTree(root)
    tree.write('raw_data.xml', encoding='utf-8', xml_declaration=True)
    print("[OK] Created raw_data.xml")

    # 4. XLSX
    print("Creating XLSX file...")
    df.to_excel('raw_data.xlsx', index=False, engine='openpyxl')
    print("[OK] Created raw_data.xlsx")

    # 5. HL7 V2
    print("Creating HL7 V2 file...")
    hl7_messages = []
    for i, record in enumerate(sample_data[:100]):  # HL7 typically has one message per patient
        # MSH segment
        msh = f"MSH|^~\\&|HIS|HOSPITAL|ADT|HOSPITAL|{datetime.now().strftime('%Y%m%d%H%M%S')}||ADT^A08^ADT_A01|{record['notice_id']}|P|2.5\r"
        # PID segment
        pid = f"PID|1||{record['abha_id']}||{record['patient_name']}^^^^|||{record['notice_date'].replace('-', '')}|||M\r"
        # PV1 segment
        pv1 = f"PV1|1|I|ICU^ICU^1|||||||||||||||||{record['consent_status']}\r"
        
        message = msh + pid + pv1
        hl7_messages.append(message)

    with open('raw_data.hl7', 'w', encoding='utf-8') as f:
        f.write('\n'.join(hl7_messages))
    print("[OK] Created raw_data.hl7")

    # 6. FHIR R5
    print("Creating FHIR R5 file...")
    fhir_bundle = {
        "resourceType": "Bundle",
        "type": "collection",
        "entry": []
    }

    for record in sample_data[:100]:  # Limit for FHIR bundle
        patient_resource = {
            "resource": {
                "resourceType": "Patient",
                "id": record['notice_id'],
                "identifier": [
                    {
                        "type": {
                            "coding": [
                                {
                                    "system": "http://terminology.hl7.org/CodeSystem/v2-0203",
                                    "code": "MR",
                                    "display": "Medical Record Number"
                                }
                            ]
                        }
                    },
                    {
                        "value": record['abha_id']
                    }
                ],
                "name": [
                    {
                        "family": record['patient_name'].split('_')[0] if '_' in record['patient_name'] else record['patient_name'],
                        "given": [record['patient_name'].split('_')[1] if '_' in record['patient_name'] else ""]
                    }
                ]
            }
        }
        
        consent_resource = {
            "resource": {
                "resourceType": "Consent",
                "id": f"consent-{record['notice_id']}",
                "status": record['consent_status'].lower(),
                "patient": {
                    "reference": f"Patient/{record['notice_id']}"
                },
                "dateTime": record['notice_date']
            }
        }
        
        fhir_bundle["entry"].append({
            "resource": patient_resource["resource"]
        })
        fhir_bundle["entry"].append({
            "resource": consent_resource["resource"]
        })

    with open('raw_data.fhir', 'w', encoding='utf-8') as f:
        json.dump(fhir_bundle, f, indent=2)
    print("[OK] Created raw_data.fhir")

    # 7. PDF
    print("Creating PDF file...")
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
        
        c = canvas.Canvas('raw_data.pdf', pagesize=letter)
        y = 750
        c.setFont("Helvetica", 10)
        
        for i, record in enumerate(sample_data[:50]):  # Limit pages
            if y < 50:
                c.showPage()
                y = 750
            
            c.drawString(50, y, f"Patient Name: {record['patient_name']}")
            y -= 15
            c.drawString(50, y, f"ABHA ID: {record['abha_id']}")
            y -= 15
            c.drawString(50, y, f"Notice ID: {record['notice_id']}")
            y -= 15
            c.drawString(50, y, f"Notice Date: {record['notice_date']}")
            y -= 15
            c.drawString(50, y, f"Consent Status: {record['consent_status']}")
            y -= 30
        
        c.save()
        print("[OK] Created raw_data.pdf")
    except ImportError:
        # Fallback: Create a text file that can be converted to PDF
        with open('raw_data_pdf.txt', 'w', encoding='utf-8') as f:
            for record in sample_data[:100]:
                f.write(f"Patient Name: {record['patient_name']}\n")
                f.write(f"ABHA ID: {record['abha_id']}\n")
                f.write(f"Notice ID: {record['notice_id']}\n")
                f.write(f"Notice Date: {record['notice_date']}\n")
                f.write(f"Consent Status: {record['consent_status']}\n")
                f.write(f"Clinical Payload: {record['clinical_payload']}\n")
                f.write("-" * 50 + "\n")
        print("[OK] Created raw_data_pdf.txt (PDF library not available, created text version)")

    # 8. Text Report
    print("Creating Text Report file...")
    with open('raw_data.txt', 'w', encoding='utf-8') as f:
        for record in sample_data:
            f.write(f"Patient Name: {record['patient_name']}\n")
            f.write(f"ABHA ID: {record['abha_id']}\n")
            f.write(f"Notice ID: {record['notice_id']}\n")
            f.write(f"Notice Date: {record['notice_date']}\n")
            f.write(f"Consent Status: {record['consent_status']}\n")
            f.write(f"Clinical Payload: {record['clinical_payload']}\n")
            f.write("=" * 50 + "\n")
    print("[OK] Created raw_data.txt")

    # 9. DICOM (create a simple text representation - actual DICOM is binary)
    print("Creating DICOM text representation...")
    with open('raw_data.dcm', 'w', encoding='utf-8') as f:
        for record in sample_data[:100]:  # Limit for DICOM
            f.write(f"(0010,0010) Patient Name: {record['patient_name']}\n")
            f.write(f"(0010,0020) Patient ID: {record['abha_id']}\n")
            f.write(f"(0008,0020) Study Date: {record['notice_date'].replace('-', '')}\n")
            f.write(f"(0020,000D) Study Instance UID: {record['notice_id']}\n")
            f.write(f"(0008,1030) Study Description: {record['clinical_payload']}\n")
            f.write("---\n")
    print("[OK] Created raw_data.dcm (text representation)")

    print("\n[OK] All sample data files created successfully!")

if __name__ == '__main__':
    main()
