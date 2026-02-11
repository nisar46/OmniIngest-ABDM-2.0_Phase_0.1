import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# Setting seed for reproducibility
np.random.seed(42)
random.seed(42)

def generate_messy_hospital_data(n_records=1000):
    """
    Generates a synthetic dataset that mimics the "Chaos" found in 
    rural hospital records (R K Nursing Home style).
    """
    
    # Base Data
    names = ["Aarav", "Vihaan", "Aditya", "Sai", "Arjun", "Ananya", "Diya", "Priya", "Sneha", "Kavya"]
    surnames = ["Sharma", "Verma", "Patel", "Reddy", "Nair", "Iyer", "Kumar", "Singh", "Yadav", "Joshi"]
    
    clinics = ["General OPD", "Labour Ward", "NICU", "Emergency", "Dental Care", "Ortho"]
    
    data = []
    
    for i in range(n_records):
        # 1. Messy Names (Case inconsistency & spelling errors)
        name = random.choice(names)
        surname = random.choice(surnames)
        full_name = f"{name} {surname}" if random.random() > 0.1 else f"{name.upper()} {surname.lower()}"
        if random.random() < 0.05: full_name = full_name.replace("a", "@") # Typo error
        
        # 2. Inconsistent Date Formats (The nightmare of hospital data)
        base_date = datetime(2020, 10, 1) + timedelta(days=random.randint(0, 1825))
        if random.random() > 0.2:
            visit_date = base_date.strftime("%Y-%m-%d")
        elif random.random() > 0.5:
            visit_date = base_date.strftime("%d/%m/%Y")
        else:
            visit_date = base_date.strftime("%b %d, %Y")
            
        # 3. Missing ABHA IDs (The compliance problem)
        abha_id = f"{random.randint(10,99)}-{random.randint(1000,9999)}-{random.randint(1000,9999)}" if random.random() > 0.3 else np.nan
        
        # 4. Outlier Billing (Manual entry errors)
        base_bill = random.randint(500, 5000)
        if random.random() < 0.02: 
            billing_amount = base_bill * 100 # An extra zero added by mistake
        elif random.random() < 0.02:
            billing_amount = -100 # Negative billing error
        else:
            billing_amount = base_bill
            
        # 5. Visit Type (OPD vs IP)
        visit_type = "OPD" if random.random() > 0.2 else "IP"
        
        # 6. Pregnancy & EDD Data (Specific for the "Leakage" problem)
        is_pregnant = "No"
        lmp_date = np.nan
        if visit_type == "OPD" and surname in ["Sharma", "Patel", "Reddy", "Nair"] and random.random() > 0.4:
            is_pregnant = "Yes"
            # Random LMP within the last 9 months
            days_ago = random.randint(10, 270)
            lmp_date = (base_date - timedelta(days=days_ago)).strftime("%Y-%m-%d")

        data.append({
            "Patient_ID": i + 1000,
            "Patient_Name": full_name,
            "Visit_Date": visit_date,
            "Visit_Type": visit_type,
            "Is_Pregnant": is_pregnant,
            "LMP_Date": lmp_date,
            "Clinic": random.choice(clinics) if random.random() > 0.1 else "Unknown",
            "ABHA_ID": abha_id,
            "Bill_Amount": billing_amount,
            "Stay_Duration_Days": random.randint(1, 10) if visit_type == "IP" else 0
        })
        
    df = pd.DataFrame(data)
    
    # Adding duplicates (The "Double Entry" problem)
    duplicates = df.sample(n=int(n_records * 0.05))
    df = pd.concat([df, duplicates], ignore_index=True)
    
    return df

if __name__ == "__main__":
    print("Starting: Generating 5 years of Hospital Operational Chaos...")
    messy_df = generate_messy_hospital_data(1000)
    
    import os
    base_path = os.path.dirname(__file__)
    file_path = os.path.join(base_path, "raw_hospital_data_2020_2025.csv")
    messy_df.to_csv(file_path, index=False)
    
    print(f"Success! File saved as {file_path}")
    print("\nSample of the 'Broken' Data:")
    print(messy_df.head(10))
    print("\nData Issues Generated:")
    print(f"- Missing ABHA IDs: {messy_df['ABHA_ID'].isna().sum()}")
    print(f"- Records with potentially wrong billing: {(messy_df['Bill_Amount'] > 50000).sum() + (messy_df['Bill_Amount'] < 0).sum()}")
