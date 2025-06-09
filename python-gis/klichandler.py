import os
import glob
import zipfile
import tempfile
import shutil
import xml.etree.ElementTree as ET

# --- Pad naar map met zip-bestanden ---
zip_folder = r"C:\Users\AL31947\OneDrive - Alliander NV\Desktop\OneDrive_1_5-6-2025"
output_base = r"C:\Users\AL31947\OneDrive - Alliander NV\Desktop\OneDrive_1_5-6-2025\klic_ssh"

# --- Namespace definitie voor GML ---
ns = {'gml': 'http://www.opengis.net/gml/3.2'}

# --- Verzamel alle zip-bestanden ---
all_zip_paths = glob.glob(os.path.join(zip_folder, "*.zip"))

# --- Verwerk in batches van max 12 ZIPs ---
batch_size = 12
for batch_index, i in enumerate(range(0, len(all_zip_paths), batch_size), start=1):
    zip_batch = all_zip_paths[i:i + batch_size]

    # Tijdelijke map per batch
    temp_dir = tempfile.mkdtemp()
    xml_files = []

    # Unzip en verzamel XML-bestanden
    for zip_path in zip_batch:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
            for root, _, files in os.walk(temp_dir):
                for file in files:
                    if file.endswith(".xml"):
                        xml_files.append(os.path.join(root, file))
                        print(f"[Batch {batch_index}] Gevonden XML: {file}")

    if not xml_files:
        print(f"[Batch {batch_index}] Geen XML-bestanden gevonden.")
        shutil.rmtree(temp_dir)
        continue

    # Gebruik eerste XML als basis
    tree_merged = ET.parse(xml_files[0])
    root_merged = tree_merged.getroot()

    # Voeg overige featureMembers toe
    for xml_file in xml_files[1:]:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        for feature_member in root.findall('gml:featureMember', ns):
            root_merged.append(feature_member)

    # Bestandsnaam bepalen en wegschrijven
    output_file = f"{output_base}_{batch_index}.xml"
    tree_merged.write(output_file, encoding='utf-8', xml_declaration=True)
    print(f"[Batch {batch_index}] Samengevoegd bestand opgeslagen als: {output_file}")

    # Opruimen temp-dir
    shutil.rmtree(temp_dir)

print("Klaar met verwerken van alle batches.")
