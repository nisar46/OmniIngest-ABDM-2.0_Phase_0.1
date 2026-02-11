import csv
import os

def year_5_compliance(file_path):
    """
    Year 5: Lead Data Analyst / Compliance Focus
    Objective: Check for DPDP Act readiness (PII scrubbing & Audit logging).
    """
    print(f"--- Year 5: DPDPA & Compliance Readiness ---")
    
    compliance_score = 0
    total_checked = 0
    
    with open(file_path, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            total_checked += 1
            # A record is "low risk" if it has an ABHA ID and clean PII tags
            if "@" not in row['Patient_Name'] and row['ABHA_ID'] != "":
                compliance_score += 1
    
    percentage = (compliance_score / total_checked) * 100
    
    print(f"\n[COMPLIANCE SUMMARY]")
    print(f"Total Records Audited: {total_checked}")
    print(f"Clean, Valid Records: {compliance_score}")
    print(f"Compliance Health: {percentage:.2f}%")
    print("-" * 50)
    
    if percentage < 70:
        print("STATUS: CRITICAL RISK. Data Quality must improve for ABDM migration.")
    else:
        print("STATUS: READY for Digital Health Transition.")

    print("-" * 50)
    print("INSIGHT: In Year 5, my focus shifted to regulatory compliance (DPDPA 2023).")
    print("ACTION: This logic is what eventually led to the development of OmniIngest 2.0.")

if __name__ == "__main__":
    base_path = os.path.dirname(__file__)
    data_file = os.path.join(base_path, "raw_hospital_data_2020_2025.csv")
    year_5_compliance(data_file)
