import pandas as pd
import os
import random
from datetime import datetime
import json

# Chemin où les données seront sauvegardées
DATA_PATH = "/tmp/space_data/dangerous_objects"

# Créer le répertoire s'il n'existe pas
os.makedirs(DATA_PATH, exist_ok=True)

# Générer des données aléatoires pour 10 objets célestes
data = []
for i in range(10):
    obj = {
        "id": f"space_{10000 + i}",
        "timestamp": int(datetime.now().timestamp()),
        "position": {
            "x": random.uniform(-1000, 1000),
            "y": random.uniform(-1000, 1000),
            "z": random.uniform(-1000, 1000)
        },
        "vitesse": random.uniform(20, 35),  # km/s
        "taille": random.uniform(5, 20),   # mètres
        "type": random.choice(["astéroïde", "comète", "météorite", "débris spatial"])
    }
    data.append(obj)

# Sauvegarde au format JSON
output_file_json = os.path.join(DATA_PATH, "sample_data.json")
with open(output_file_json, 'w') as f:
    json.dump(data, f)

# Lire les données depuis JSON pour préserver la structure exacte
df = pd.read_json(output_file_json)

# Sauvegarde au format Parquet
output_file = os.path.join(DATA_PATH, "sample_data.parquet")
df.to_parquet(output_file, index=False)

print(f"Données d'exemple générées et sauvegardées dans {output_file}")