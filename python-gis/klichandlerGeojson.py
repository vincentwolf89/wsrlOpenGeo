import os
import json
from collections import defaultdict

# 📁 Pad naar map met de losse geojsons
input_folder = r"C:\Users\AL31947\OneDrive - Alliander NV\Desktop\OneDrive_1_5-6-2025\exports"
output_folder = r"C:\Users\AL31947\OneDrive - Alliander NV\Desktop\OneDrive_1_5-6-2025\exports\merge"  # eventueel dezelfde

# 📂 Verzamel bestanden per thema
thema_bestanden = defaultdict(list)

for filename in os.listdir(input_folder):
    if filename.endswith(".geojson"):
        thema = filename.split("_")[0]  # alles vóór "_"
        thema_bestanden[thema].append(os.path.join(input_folder, filename))

# 🔁 Merge per thema
for thema, bestanden in thema_bestanden.items():
    merged_features = []

    for path in bestanden:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
            features = data.get("features", [])
            merged_features.extend(features)

    geojson = {
        "type": "FeatureCollection",
        "features": merged_features
    }

    output_path = os.path.join(output_folder, f"{thema}.geojson")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(geojson, f, indent=2)

    print(f"✔️ Samengevoegd: {output_path}")

    