"""
Test script to test universal_adapter.py with all formats
"""

import subprocess
import os
from pathlib import Path

# List of test files
test_files = [
    'raw_data.csv',
    'raw_data.json',
    'raw_data.xml',
    'raw_data.xlsx',
    'raw_data.hl7',
    'raw_data.fhir',
    'raw_data.txt'
]

print("Testing universal_adapter.py with all formats...")
print("=" * 60)

# First, remove or rename the output file if it exists
output_file = 'standardized_ingress_1000.csv'
if Path(output_file).exists():
    if Path(f'{output_file}.bak').exists():
        os.remove(f'{output_file}.bak')
    os.rename(output_file, f'{output_file}.bak')

# Test each format
for test_file in test_files:
    if not Path(test_file).exists():
        print(f"\n[SKIP] {test_file} - File not found")
        continue
    
    print(f"\n[TEST] Testing with {test_file}...")
    print("-" * 60)
    
    # Temporarily rename other files to test only this one
    # Also exclude the output file and hide all other raw_data files
    all_raw_files = list(Path('.').glob('raw_data.*'))
    other_files = [f for f in all_raw_files if f.name != test_file and f.name != output_file]
    renamed = []
    
    for other_file in other_files:
        bak_name = f"{other_file.name}.bak"
        if Path(other_file).exists():
            try:
                os.rename(str(other_file), bak_name)
                renamed.append((str(other_file), bak_name))
            except:
                pass
    
    # Also hide the output file if it exists
    output_hidden = False
    if Path(output_file).exists():
        try:
            os.remove(output_file)  # Remove it before test
            output_hidden = True
        except:
            pass
    
    try:
        # Run the adapter
        result = subprocess.run(['python', 'universal_adapter.py'], 
                              capture_output=True, text=True, encoding='utf-8', errors='replace')
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        if result.returncode == 0:
            print(f"[OK] {test_file} - Test passed!")
        else:
            print(f"[FAIL] {test_file} - Test failed with return code {result.returncode}")
    except Exception as e:
        print(f"[ERROR] {test_file} - Exception: {str(e)}")
    finally:
        # Restore renamed files
        for original, bak in renamed:
            if Path(bak).exists():
                try:
                    if Path(original).exists():
                        os.remove(original)
                    os.rename(bak, original)
                except:
                    pass
    
    print("-" * 60)

print("\n" + "=" * 60)
print("Testing complete!")
