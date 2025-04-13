import re

filename = "98_0707100000378704 Lekdijk B 76 Lek.pdf"

# Regular expression to match the city name at the end, capturing all words before `.pdf`
match = re.search(r'\d+\s+\D+\s+\d+\s*(?:[A-Z]?\s+)?(.+?)\.pdf$', filename)


# Check if a match is found
if match:
    city_name = match.group(1).strip()  # Remove any leading/trailing spaces
    print("City name:", city_name)
else:
    print("City name not found.")