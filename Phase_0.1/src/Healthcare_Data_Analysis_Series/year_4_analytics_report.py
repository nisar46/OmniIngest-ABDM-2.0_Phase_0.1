import csv
import os

def year_4_analytics(file_path):
    """
    Year 4: Data Analyst (Ops) Focus
    Objective: Summarize hospital performance by clinic (Volume & Revenue).
    """
    print(f"--- Year 4: Hospital Operations Analytics ---")
    
    clinic_stats = {} # Using a dictionary to count patients and revenue
    
    with open(file_path, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            clinic = row['Clinic']
            try:
                bill = float(row['Bill_Amount'])
            except ValueError:
                bill = 0

            if clinic not in clinic_stats:
                clinic_stats[clinic] = {'count': 0, 'revenue': 0}
            
            clinic_stats[clinic]['count'] += 1
            clinic_stats[clinic]['revenue'] += bill

    print(f"\n[REPORT COMPLETE] 5-Year Performance Summary by Department")
    print("-" * 60)
    print(f"{'Clinic Name':<20} | {'Patients':<10} | {'Total Revenue'}")
    print("-" * 60)
    
    # Sort by patient volume
    sorted_clinics = sorted(clinic_stats.items(), key=lambda x: x[1]['count'], reverse=True)

    for clinic, stats in sorted_clinics:
        print(f"{clinic:<20} | {stats['count']:<10} | INR {stats['revenue']:,.2f}")

    print("-" * 60)
    print("INSIGHT: In Year 4, I started using Python dictionaries to provide 'Business Intelligence'.")
    print("ACTION: This data helped the management decide where to hire more nurses.")

if __name__ == "__main__":
    base_path = os.path.dirname(__file__)
    data_file = os.path.join(base_path, "raw_hospital_data_2020_2025.csv")
    year_4_analytics(data_file)
