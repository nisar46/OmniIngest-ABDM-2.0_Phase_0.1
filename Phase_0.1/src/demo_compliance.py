import pandas as pd
import time
from compliance_engine import ComplianceEngine, PIIVault

def run_simulation():
    print("="*60)
    print("  OMNI-INGEST: COMPLIANCE ENGINE IMPLEMENTATION (v2.0)")
    print("  Target Governance: India DPDP 2026 / Budget Clause 4")
    print("="*60)
    
    # Initialize Engine
    print("\n[INIT] Initializing Compliance Rules Engine...")
    engine = ComplianceEngine(threshold_days=365) # 1 year retention policy
    vault = PIIVault()
    time.sleep(1)
    print("[INIT] Policy Loaded: RETENTION_PERIOD = 365 Days")
    print("[INIT] Policy Loaded: AUTOMATED_PURGE = ENABLED")

    # Mock Data Batch
    print("\n[DATA] Ingesting Mock Data Batch for Processing...")
    mock_data = [
        {
            "Patient_Name": "Amit Sharma", 
            "ABHA_ID": "12-3456-7890-1234", 
            "Consent_Status": "GRANTED", 
            "Notice_Date": "2025-12-01", # Recent
            "Data_Purpose": "Treatment"
        },
        {
            "Patient_Name": "Priya Verma", 
            "ABHA_ID": "98-7654-3210-9876", 
            "Consent_Status": "REVOKED", # Should be purged
            "Notice_Date": "2025-06-15",
            "Data_Purpose": "Research"
        },
        {
            "Patient_Name": "Rahul Singh", 
            "ABHA_ID": "55-5555-5555-5555", 
            "Consent_Status": "GRANTED", 
            "Notice_Date": "2023-01-01", # Expired (>365 days)
            "Data_Purpose": "Audit"
        },
        {
             "Patient_Name": "Sneha Gupta",
             "ABHA_ID": "11-2222-3333-4444",
             "Consent_Status": "GRANTED",
             "Notice_Date": "2026-01-15",
             "Data_Purpose": "Marketing" # Unauthorized Purpose
        }
    ]

    df = pd.DataFrame(mock_data)
    print(f"[DATA] Loaded {len(df)} records.")
    
    # Process
    print("\n[PROCESS] Running Compliance Evaluation & Pseudonymization...")
    processed_rows = []
    
    for _, row in df.iterrows():
        # Convert to dict for processing
        record = row.to_dict()
        
        # 1. Apply Purge Logic (DPDP Rule 8)
        record = engine.apply_purge(record)
        
        # 2. Apply Pseudonymization (Budget 2026 AI Gov)
        # Only if not already purged
        if record.get("_Ingest_Status", "").startswith("SUCCESS"):
            record = engine.pseudonymize_pii(record)
            
        processed_rows.append(record)
        time.sleep(0.5) # Simulate processing time

    # Results
    result_df = pd.DataFrame(processed_rows)
    
    print("\n" + "="*60)
    print("  COMPLIANCE AUDIT REPORT GENERATED")
    print("="*60)
    
    print("\n[SUMMARY]")
    print(result_df[['Consent_Status', 'Notice_Date', '_Ingest_Status']])

    print("\n[PII SAFETY CHECK]")
    print(result_df[['Patient_Name', 'ABHA_ID']])
    
    print("\n[SECURITY]")
    print(vault.shred_keys())
    print("="*60)
    print("  SIMULATION COMPLETE")
    print("="*60)

if __name__ == "__main__":
    run_simulation()
