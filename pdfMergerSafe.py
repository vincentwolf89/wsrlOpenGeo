import os
from PyPDF2 import PdfReader, PdfWriter

# Functie om een pdf te laden vanaf een gegeven pad
def load_pdf(file_path):
    with open(file_path, "rb") as file:
        reader = PdfReader(file)
        return reader

# Functie om een nieuwe pdf te schrijven
def save_pdf(writer, output_path):
    with open(output_path, "wb") as file:
        writer.write(file)

# Functie om pagina's van een PDF te verwijderen (zoals de lege pagina)
def remove_empty_page(reader, page_number_to_remove):
    writer = PdfWriter()
    for i in range(len(reader.pages)):
        if i != page_number_to_remove:  # Skip de lege pagina
            writer.add_page(reader.pages[i])
    return writer

# Functie om PDF's samen te voegen
def merge_pdfs(pdf_readers):
    writer = PdfWriter()
    for reader in pdf_readers:
        for page in reader.pages:
            writer.add_page(page)
    return writer

# Functie om de vereiste factsheet, algemene rapportage en bouwrisk samen te voegen
def create_combined_pdf(factsheet_path, general_report_path, bouwrisk_path, output_path):
    # Laad de factsheet
    factsheet_pdf = load_pdf(factsheet_path)

    # Laad de algemene rapportage
    general_report_pdf = load_pdf(general_report_path)

    # Verwijder de lege pagina (pagina 6)
    general_report_writer = remove_empty_page(general_report_pdf, 5)  # Aangenomen dat pagina's vanaf 0 beginnen

    # Voeg de factsheet op pagina 6 toe
    general_report_writer.add_page(factsheet_pdf.pages[0])

    # Laad de bouwrisk rapportage
    bouwrisk_pdf = load_pdf(bouwrisk_path)

    # Voeg bouwrisk rapportage toe achter de algemene rapportage
    combined_writer = merge_pdfs([general_report_writer, bouwrisk_pdf])

    # Sla de samengevoegde PDF op
    save_pdf(combined_writer, output_path)

# Functie om door de algemene rapportages te itereren en deze samen te voegen met factsheet en bouwrisk
def process_all_reports(general_report_dir, factsheet_dir, bouwrisk_base_dir, output_dir):
    for filename in os.listdir(general_report_dir):
        if filename.endswith(".pdf"):
            # Voorbeeld: extracteer bag_id of nummer uit de bestandsnaam (hier wordt aangenomen dat dit in de naam zit)
            bag_id = filename.split('_')[0]  # Pas dit aan op basis van je bestandsnaamconventie

            # Genereer de paden naar de factsheet en bouwrisk op basis van bag_id
            factsheet_path = os.path.join(factsheet_dir, f"{bag_id}.pdf")

            # Bouwrisk pad vinden (de submap met het bag_id als naam of nummer)
            bouwrisk_path = os.path.join(bouwrisk_base_dir, bag_id, "Visuele inspectie", f"bouwrisk_{bag_id}.pdf")

            # Volledig pad naar de algemene rapportage
            general_report_path = os.path.join(general_report_dir, filename)

            # Output-bestandsnaam instellen
            straat = "Hoofdstraat"  # Pas dit aan naar hoe je straat en plaats gegevens wilt ophalen
            huisnummer = "10"       # Dit kan ook dynamisch zijn op basis van de bestandsnaam
            plaats = "Amsterdam"    # Eveneens dynamisch aanpasbaar
            output_filename = f"Rapport_belending_informatie_{bag_id}_{straat}_{huisnummer}_{plaats}.pdf"
            output_path = os.path.join(output_dir, output_filename)

            # Combineer de documenten en sla op
            print(f"Verwerken van: {general_report_path}")
            create_combined_pdf(factsheet_path, general_report_path, bouwrisk_path, output_path)

            print(f"Document succesvol opgeslagen als {output_filename}")

# Padinstellingen
general_report_dir = "/pad/naar/01 Visuele inspecties & Archief/Dijkzone_1/"
factsheet_dir = "/pad/naar/SAFE/NR_ADRES_BAGID/Alle_documenten/"
bouwrisk_base_dir = "/pad/naar/01 Visuele inspecties & Archief/Dijkzone_1/"
output_dir = "/pad/naar/output/directory"

# Verwerk alle rapportages in de opgegeven directory
process_all_reports(general_report_dir, factsheet_dir, bouwrisk_base_dir, output_dir)
