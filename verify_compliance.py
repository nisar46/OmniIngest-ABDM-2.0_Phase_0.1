
import re
import os

def verify_compliance():
    print("Beginning Verification...\n")
    
    # Check Ingress Regex
    try:
        with open(r"d:\Omnigest_ABDM_2.0\ingress.py", "r", encoding='utf-8') as f:
            ingress_content = f.read()
            
        expected_regex = r"([0-9]{2}-[0-9]{4}-[0-9]{4}-[0-9]{4}|[a-zA-Z0-9.]+@sbx)"
        if expected_regex in ingress_content:
            print("[OK] ingress.py: Sandbox Regex Verified.")
        else:
            print("[FAIL] ingress.py: Sandbox Regex NOT found.")
    except Exception as e:
        print(f"[ERROR] Reading ingress.py: {e}")
        
    # Check App FHIR URL
    try:
        with open(r"d:\Omnigest_ABDM_2.0\app.py", "r", encoding='utf-8') as f:
            app_content = f.read()
            
        if "https://healthidsbx.abdm.gov.in" in app_content:
            print("[OK] app.py: FHIR Sandbox URL Verified.")
        else:
            print("[FAIL] app.py: FHIR Sandbox URL NOT found.")
            
        # Check App Header Msg
        if "X-CM-ID: sbx" in app_content:
            print("[OK] app.py: X-CM-ID Visual Status Verified.")
        else:
             print("[FAIL] app.py: X-CM-ID Visual Status NOT found.")
             
        # Check Purge Logic
        if "DPDP Rule 8.2: Erasure Notice Sent" in app_content and ("purge_pending" in app_content):
            print("[OK] app.py: Rule 8.2 Purge Logic Verified.")
        else:
            print("[FAIL] app.py: Rule 8.2 Purge Logic NOT found.")
            
    except Exception as e:
         print(f"[ERROR] Reading app.py: {e}")
        
if __name__ == "__main__":
    verify_compliance()
