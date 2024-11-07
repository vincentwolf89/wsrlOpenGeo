import re

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
            # The city name comes after the first word that starts with a capital letter (presumably the city name)
            address = re.sub(r"\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*$", "", address)
            return address
    
    if match:
        return match.group(1).strip()  # Return the extracted address part
    return None


# Test examples for Folder 1 and Folder 2
folder1_files = [
    "7279 Achthoven 20 VO BU KRJ280623.pdf",  # Expected: 'Achthoven 20'
    "1234 Main St 5 VO BU KRJ280623.pdf"      # Expected: 'Main St 5'
]

folder2_files = [
    "177_1978100007672212 Lekdijk 27 Langerak.pdf",  # Expected: 'Lekdijk 27'
    "195_0694100000000189 Bergstoep 12 Streefkerk.pdf",  # Expected: 'Bergstoep 12'
    "96_0707100000378256 Kerkpad 1 Tienhoven aan de Lek.pdf"  # Expected: 'Kerkpad 1'
]

# Test Folder 1
for filename in folder1_files:
    address = extract_address(filename, "folder1")
    print(f"Folder1 - Filename: {filename}, Extracted Address: {address}")

# Test Folder 2
for filename in folder2_files:
    address = extract_address(filename, "folder2")
    print(f"Folder2 - Filename: {filename}, Extracted Address: {address}")
