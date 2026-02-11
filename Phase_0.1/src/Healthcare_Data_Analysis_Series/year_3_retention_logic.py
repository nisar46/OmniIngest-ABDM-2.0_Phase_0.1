import csv
from datetime import datetime, timedelta

def calculate_edd(lmp_str):
    """
    Calculates Expected Date of Delivery (EDD) using Naegele's Rule:
    LMP + 9 months + 7 days (simplified as LMP + 280 days)
    """
    if not lmp_str or lmp_str == "":
        return None
    
    # Try different date formats commonly found in hospital data
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%b %d, %Y"):
        try:
            lmp_date = datetime.strptime(lmp_str, fmt)
            edd_date = lmp_date + timedelta(days=280)
            return edd_date
        except ValueError:
            continue
    return None

def track_edd_leakage(file_path):
    print(f"--- Processing Patient Records: {file_path} ---")
    
    pregnant_patients = []
    ip_admissions = []
    
    # 1. Step: Read the file and categorize patients
    with open(file_path, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row['Is_Pregnant'] == "Yes":
                pregnant_patients.append(row)
            if row['Visit_Type'] == "IP":
                ip_admissions.append(row['Patient_Name'])

    # 2. Step: Logic to check for "Leakage"
    # We define a leak as: A pregnant patient who hasn't been admitted (IP) yet.
    
    print(f"\n[ALERT] Found {len(pregnant_patients)} Pregnant Patients in OPD.")
    print("-" * 50)
    print(f"{'Patient Name':<20} | {'LMP Date':<15} | {'EDD Date':<15} | {'Status'}")
    print("-" * 50)

    leaked_count = 0
    
    for patient in pregnant_patients:
        name = patient['Patient_Name']
        lmp = patient['LMP_Date']
        edd = calculate_edd(lmp)
        
        if edd:
            edd_str = edd.strftime("%d-%b-%Y")
            
            # Check if this name exists in IP admissions
            if name in ip_admissions:
                status = "SECURED (Admitted)"
            else:
                status = "LEAKAGE RISK (No IP Visit)"
                leaked_count += 1
                
            print(f"{name:<20} | {lmp:<15} | {edd_str:<15} | {status}")
        else:
            print(f"{name:<20} | {lmp:<15} | {'INVALID DATE':<15} | ⚠️ CHECK LMP")

    print("-" * 50)
    print(f"SUMMARY: {leaked_count} patients are at risk of delivering at another hospital.")
    print(f"IMPACT: If we retain these {leaked_count} patients, hospital revenue increases significantly.")

if __name__ == "__main__":
    import os
    base_path = os.path.dirname(__file__)
    data_file = os.path.join(base_path, "raw_hospital_data_2020_2025.csv")
    track_edd_leakage(data_file)
