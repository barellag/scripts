#Created by Gabriel Barella

#Purpose of this is to extract nested zip files, since Veeam logs use nested zips (zips within zips).

import os
import zipfile
import sys

#function to extract files even if they are nested
def extract_zip(full_path, dir_name):
    """extract a zip file"""
    print(f"Extracting {full_path}...")
    sys.stdout.flush()
    with zipfile.ZipFile(full_path, "r") as zip_ref:
        zip_ref.extractall(dir_name)
    os.remove(full_path)
    print(f"Finished extracting and deleted {full_path}")
    sys.stdout.flush()

def unzip_all_in_dir(dir_name):
    """Recursively go through directories and unzip any files."""
    file_counter = 0

    for item in os.listdir(dir_name):
        full_path = os.path.join(dir_name, item)

        if zipfile.is_zipfile(full_path):   
            file_counter += 1
            print(f'Processing {file_counter} - {full_path}')
            sys.stdout.flush() # and this
            extract_zip(full_path, dir_name)
            # Recurse in the same dir to handle the case where the extracted files are zip files.
            unzip_all_in_dir(dir_name)

        elif os.path.isdir(full_path):
            unzip_all_in_dir(full_path)
            
#get directory
directoryToExtract = input("Enter the directory where your zip file is: ")
unzip_all_in_dir(directoryToExtract)
