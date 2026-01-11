"""
Phase 0 Scaffold Script
Orchestrates the data ingestion workflow:
1. Generate sample data
2. Organize raw data into folders
3. Standardize data using Universal Adapter
"""

import subprocess
import sys
import os
import time

def run_step(script_name, description):
    """Run a python script and check for success"""
    print(f"\n{'='*60}")
    print(f"STEP: {description}")
    print(f"Running {script_name}...")
    print(f"{'='*60}\n")
    
    start_time = time.time()
    
    try:
        result = subprocess.run([sys.executable, script_name], check=True)
        duration = time.time() - start_time
        print(f"\n[SUCCESS] {script_name} completed in {duration:.2f} seconds.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n[ERROR] {script_name} failed with exit code {e.returncode}.")
        return False
    except Exception as e:
        print(f"\n[ERROR] Failed to run {script_name}: {str(e)}")
        return False

def main():
    print("Starting Phase 0 Workflow...")
    
    # Step 1: Generate Sample Data
    if not run_step('create_sample_data.py', "Generating Sample Data"):
        sys.exit(1)
        
    # Step 2: Organize Data
    if not run_step('organize_raw_data.py', "Organizing Raw Data"):
        sys.exit(1)
        
    # Step 3: Run Ingestion/Standardization
    if not run_step('universal_adapter.py', "Standardizing Data (Ingestion)"):
        sys.exit(1)
        
    print("\n" + "="*60)
    print("PHASE 0 COMPLETED SUCCESSFULLY")
    print("="*60)
    print("Output file: standardized_ingress_1000.csv")

if __name__ == "__main__":
    main()
