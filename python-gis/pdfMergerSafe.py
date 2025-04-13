import os
import re
from PyPDF2 import PdfFileReader, PdfFileWriter
from collections import Counter

def extract_address(filename, folder):
    if folder == "folder1":
        # Folder 1 format: Extract address (street name and number) before any suffix like 'VO', 'BU', 'KRJ', etc.
        match = re.search(r"(\D+\s+\d+\s*\w?)(?=\s+(?:VO\s+BU|\s+KRJ|\s*$))", filename)
    
    elif folder == "folder2":
        # Folder 2 format: Skip the first numerical part (e.g., '96_0707100000378256') and capture street name and number
        # Extract street name and number, ensuring we stop before the city name starts
        match = re.search(r"\d+_\d+\s+([A-Za-z\s]+\d+\s*\w?)(?=\s+[A-Za-z\s]+\.pdf$)", filename)

        # Additional refinement to remove city names if present
        if match:
            address = match.group(1).strip()
            # Remove any city name from the end (multiple words after the street name and number)
            address = re.sub(r"\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*$", "", address)
            return address
    
    if match:
        return match.group(1).strip()  # Return the extracted address part
    return None


def merge_pdfs(main_pdf_path, folder1_path, folder2_path, output_dir):
    # Load the main PDF as a template
    main_pdf = PdfFileReader(main_pdf_path)

    unique_list = []
    written_files = []
    
    # List to store unmerged file names
    unmerged_files = []

    # Loop over each file in the first folder
    for file1 in os.listdir(folder1_path):
        if file1.endswith(".pdf"):
            # Extract the address from the filename
            address = extract_address(file1, "folder1")
            city_name = ""
            unique_list.append(address)
            # print(f"Extracted address from folder1: {address}")
            if not address:
                print(f"Could not extract address from '{file1}'")
                continue
            
            file1_path = os.path.join(folder1_path, file1)
            
            # Initialize a writer for the new PDF based on the main PDF template
            writer = PdfFileWriter()
            for page in main_pdf.pages:
                writer.addPage(page)


            # Add the current file from folder1 at the start of the new PDF
            file1_pdf = PdfFileReader(file1_path)
            for page in file1_pdf.pages:
                writer.addPage(page)

            # Add PDFs from folder2 that match the current address
            added_pages_from_folder2 = False  # Flag to check if pages from folder2 are added
            for file2 in os.listdir(folder2_path):
                if file2.endswith(".pdf"):


                   
                    # Extract address from each file2 filename
                    file2_address = extract_address(file2, "folder2")
                    # print(f"Checking file2 '{file2}' with extracted address '{file2_address}'")

                    # Check if addresses match
                    if file2_address == address:

                        test_name = re.search(r'\d+\s+\D+\s+\d+(?:\s+[A-Z]|\s+\d+)*\s+(.+?)\.pdf$', file2)

                        # Check if a match is found
                        if test_name:
                            city_name = test_name.group(1)
                            print("City name:", city_name)
                        else:
                            # print("City name not found.")
                            pass

                        file2_path = os.path.join(folder2_path, file2)
                        file2_pdf = PdfFileReader(file2_path)
                        # print(f"Adding pages from {file2_path}...")

                        # Append each page from this matching file in folder2
                        for page in file2_pdf.pages:
                            writer.addPage(page)
                        added_pages_from_folder2 = True  # Mark that pages were added from folder2

            # If no pages from folder2 were added, print a message
            if not added_pages_from_folder2:
                # print(f"No matching files from folder2 for address '{address}'.")
                unmerged_files.append(file1)  # Add to the list of unmerged files



            # Save the new PDF to the output directory
            output_path= os.path.join(output_dir, f"Rapport_belendingen_informatie_{address}_{city_name}.pdf")
            output_path = output_path.replace(" ", "_")

            with open(output_path, "wb") as output_file:
                written_files.append(output_path)
                writer.write(output_file)
                

            # print(f"Created merged PDF for address '{address}' at '{output_path}'")

    print (len(written_files), "files merged successfully.")
    counter = Counter(unique_list)
    duplicates = [item for item, count in counter.items() if count > 1]

    print("Duplicates:", duplicates)  # Output will be [1, 5, 3]


# Define paths
main_pdf_path = r"C:\Users\vince\Desktop\pdfmerger_laura\Rapport belendingen informatie.pdf"        
folder1_path = r"C:\Users\vince\Desktop\pdfmerger_laura\Rapport Bouwrisk"        
folder2_path = r"C:\Users\vince\Desktop\pdfmerger_laura\Factsheets_adres"           
output_dir = r"C:\Users\vince\Desktop\pdfmerger_laura\output"      

# Run the merging process
merge_pdfs(main_pdf_path, folder1_path, folder2_path, output_dir)
