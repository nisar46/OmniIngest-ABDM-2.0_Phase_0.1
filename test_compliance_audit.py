import pandas as pd
from compliance_engine import ComplianceEngine

def run_audit_test():
    engine = ComplianceEngine()
    
    print("--- 2026 COMPLIANCE AUDIT TEST SUITE ---")
    
    # 1. Regex Validation Test
    print("\n[STEP 1] Notice_ID Regex Validation")
    test_ids = [
        ("N-2026-CONS-v1.1", True),   # Valid 2026
        ("N-2026-ADIT-v2.0", True),   # Valid 2026
        ("N-2025-CONS-v1.0", False),  # Legacy 2025 (Rejected)
        ("ABC12345", False),          # Legacy Phase 0.1 (Rejected)
        ("N-2026-MARK-v1", False),    # Invalid version format
    ]
    
    for nid, expected in test_ids:
        is_valid = engine.validate_notice_id(nid)
        status = "PASS" if is_valid == expected else "FAIL"
        print(f"  - {nid}: {'Valid' if is_valid else 'Invalid'} (Expected: {'Valid' if expected else 'Invalid'}) -> {status}")

    # 2. PII Masking & Hard-Purge Simulation (Rule 8)
    print("\n[STEP 2] Rule 8 Partial Purge Simulation")
    # Simulate a record with revoked consent
    test_record = pd.Series({
        'Patient_Name': 'John Doe',
        'ABHA_ID': 'ABHA123456789',
        'Clinical_Payload': '{"diagnosis": "Viral Fever", "vitals": "Normal"}',
        'Consent_Status': 'REVOKED',
        'Notice_Date': '2026-01-01',
        'Data_Purpose': 'Consultation'
    })
    
    print("  BEFORE PURGE:")
    print(f"    Name: {test_record['Patient_Name']}")
    print(f"    ABHA: {test_record['ABHA_ID']}")
    print(f"    Clinical Payload: {test_record['Clinical_Payload']}")
    
    # Apply Purge
    purged_record = engine.apply_purge(test_record)
    
    print("\n  AFTER PURGE (Partial Purge Check):")
    print(f"    Name: {purged_record['Patient_Name']} (Expected: REDACTED)")
    print(f"    ABHA: {purged_record['ABHA_ID']} (Expected: REDACTED)")
    print(f"    Clinical Payload: {purged_record['Clinical_Payload']} (Expected: PURGED_DPDP_RULE_8_ERASURE)")
    
    # Audit Trace Check (Hashing)
    print("\n[STEP 3] Audit Trail Traceability")
    trace_id = engine.hash_id("ABHA123456789")
    print(f"  Stable Trace Hash: {trace_id} (Safe for logs, verifiable against master index)")

if __name__ == "__main__":
    run_audit_test()
