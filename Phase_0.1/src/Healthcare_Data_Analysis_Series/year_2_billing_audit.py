import csv
import os

def year_2_billing_audit(file_path):
    """
    Year 2: Resource In-charge / Billing Focus
    Objective: Find revenue leakage and billing outliers (Extra zeros, Negative bills).
    """
    print(f"--- Year 2: Revenue & Billing Audit ---")
    
    billing_issues = []
    total_leaked_revenue = 0
    
    with open(file_path, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            try:
                bill = float(row['Bill_Amount'])
            except ValueError:
                continue

            issue = None
            if bill > 50000:
                issue = "Potential Extra Zero Error"
            elif bill < 0:
                issue = "Negative Bill Error"
            elif bill == 0:
                issue = "Unbilled Visit"

            if issue:
                row['Billing_Issue'] = issue
                billing_issues.append(row)
                if bill < 0 or bill == 0:
                    total_leaked_revenue += 1000 # Estimated loss per unbilled visit

    print(f"\n[AUDIT COMPLETE] Found {len(billing_issues)} billing anomalies.")
    print("-" * 90)
    print(f"{'Patient ID':<12} | {'Patient Name':<20} | {'Amount':<10} | {'Issue Found'}")
    print("-" * 90)
    
    for record in billing_issues[:15]:
        print(f"{record['Patient_ID']:<12} | {record['Patient_Name']:<20} | {record['Bill_Amount']:<10} | {record['Billing_Issue']}")

    print("-" * 90)
    print(f"INSIGHT: In Year 2, I found that small manual errors were costing the hospital thousands.")
    print(f"ACTION: I built this simple check to audit daily finance reports.")

if __name__ == "__main__":
    base_path = os.path.dirname(__file__)
    data_file = os.path.join(base_path, "raw_hospital_data_2020_2025.csv")
    year_2_billing_audit(data_file)
