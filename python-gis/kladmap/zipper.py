import os
import zipfile

# Specify the directory containing the folders you want to zip
directory_path = r'C:\Users\vince\Desktop\wetransfer_safe-stbi-niet-prio-vakken_2023-08-21_1517\230818_STBI_niet-prio_GIS'

# Iterate through the folders in the directory
for folder_name in os.listdir(directory_path):
    folder_path = os.path.join(directory_path, folder_name)
    
    # Check if the item in the directory is a folder
    if os.path.isdir(folder_path):
        # Create a separate ZIP file for each folder
        zip_file_name = folder_name + '.zip'
        zip_file_path = os.path.join(directory_path, zip_file_name)
        
        # Create a ZIP file and add the contents of the folder to it
        with zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, folder_path)
                    zipf.write(file_path, arcname)

print("All folders zipped successfully.")