import pandas as pd
import requests
from io import StringIO

# Anni da 2526 indietro fino a 1819 (8 stagioni)
years = [f"{y}{y+1}" for y in range(18, 26)]

# Campionati
leagues = [
    "E0","E1","E2","E3","SC0","SC1",
    "D1","D2","I1","I2",
    "SP1","SP2","F1","F2",
    "N1","B1","P1","T1","G1"
]

base_url = "https://www.football-data.co.uk/mmz4281/{}/{}.csv"

columns_per_file = {}

for year in years:
    for league in leagues:
        url = base_url.format(year, league)
        try:
            r = requests.get(url, timeout=10)
            if r.status_code == 200 and len(r.text) > 100:
                df = pd.read_csv(StringIO(r.text))
                cols = set(df.columns)
                columns_per_file[f"{year}_{league}"] = cols
                print(f"{year}_{league}: {len(cols)} colonne")
            else:
                print(f"Skip {url} (vuoto o non trovato)")
        except Exception as e:
            print(f"Errore {url}: {e}")

# Intersezione globale
if columns_per_file:
    all_sets = list(columns_per_file.values())
    common_cols = set.intersection(*all_sets)
    print("\n=== Colonne comuni a tutti i file ===")
    for c in sorted(common_cols):
        print(c)
else:
    print("Nessun file valido scaricato.")
