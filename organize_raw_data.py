import os
import shutil
import glob

def organize_data():
    """Organize raw data files into specific folders for processing"""
    print("Organizing raw data files...")
    
    # Define mapping of extensions to folders
    folder_map = {
        '.csv': 'raw_data_csv',
        '.json': 'raw_data_json',
        '.xml': 'raw_data_xml',
        '.xlsx': 'raw_data_xlsx',
        '.hl7': 'raw_data_hl7',
        '.fhir': 'raw_data_fhir',
        '.dcm': 'raw_data_dicom',
        '.txt': 'raw_data_txt'
    }
    
    # Create folders if they don't exist
    for folder in folder_map.values():
        if not os.path.exists(folder):
            os.makedirs(folder)
            
    # Move files
    files_moved = 0
    for file in os.listdir('.'):
        if file.startswith('raw_data') and os.path.isfile(file):
            ext = os.path.splitext(file)[1].lower()
            if ext in folder_map:
                dest_folder = folder_map[ext]
                shutil.copy(file, os.path.join(dest_folder, file))
                files_moved += 1
                
    print(f"Organized {files_moved} files into subdirectories.")

if __name__ == "__main__":
    organize_data()
