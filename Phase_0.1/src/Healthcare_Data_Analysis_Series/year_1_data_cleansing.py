# --- WHAT THIS SCRIPT DOES ---
# 1. It opens the dummy hospital file.
# 2. It goes line-by-line looking for mistakes.
# 3. It prints a list of the mistakes it found so you can fix them.

import csv
import os

def year_1_cleaning(file_path):
    print(f"--- Year 1: Finding Basic Mistakes in Hospital Records ---")
    
    # We will keep all the messy records in this empty list
    messy_records = []
    
    # Open the file and start reading
    with open(file_path, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            issues = []
            
            # CHECK 1: Is the name in ALL CAPS or all lower case?
            # Hospital staff should use "Proper Case" (like Nisar Ahmed)
            if row['Patient_Name'] != row['Patient_Name'].title():
                issues.append("Capitalization Mistake")
            
            # CHECK 2: Is there a weird character like '@' in the name?
            # This happens when people type too fast.
            if "@" in row['Patient_Name']:
                issues.append("Typo found (@)")
                
            # CHECK 3: Is the ABHA ID empty?
            # This is a common mistake when doctors forget to ask patients.
            if not row['ABHA_ID'] or row['ABHA_ID'] == "":
                issues.append("Missing ID")
            
            # If we found any of the issues above, save this patient's info
            if issues:
                row['Issues_Found'] = ", ".join(issues)
                messy_records.append(row)

    # Now, let's show you what we found!
    print(f"\n[DONE] I found {len(messy_records)} patients with mistakes.")
    print("-" * 80)
    print(f"{'Patient ID':<12} | {'Patient Name':<20} | {'What is wrong?'}")
    print("-" * 80)
    
    # Let's print the first 15 mistakes we found
    for record in messy_records[:15]:
        print(f"{record['Patient_ID']:<12} | {record['Patient_Name']:<20} | {record['Issues_Found']}")

    print("-" * 80)
    print("MY JOURNEY LOG: In Year 1, I saw that humans make lots of typos.")
    print("THIS SCRIPT saved me hours because I didn't have to check 1,000 files by hand.")

if __name__ == "__main__":
    import os
    # Get the directory where this script is located
    base_path = os.path.dirname(__file__)
    data_file = os.path.join(base_path, "raw_hospital_data_2020_2025.csv")
    
    year_1_cleaning(data_file)
