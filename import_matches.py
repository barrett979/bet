import pandas as pd
import requests
from io import StringIO
from sqlalchemy import create_engine, text

# Connessione a Postgres (modifica con la tua password!)
DATABASE_URL = "postgresql://postgres:Vasco!31@localhost:5432/bet"
engine = create_engine(DATABASE_URL)

# Anni da 1819 fino a 2526 (8 stagioni)
years = [f"{y}{y+1}" for y in range(18, 26)]

# Campionati
leagues = [
    "E0","E1","E2","E3","SC0","SC1",
    "D1","D2","I1","I2",
    "SP1","SP2","F1","F2",
    "N1","B1","P1","T1","G1"
]

base_url = "https://www.football-data.co.uk/mmz4281/{}/{}.csv"

# Mappa colonne CSV → colonne DB
col_map = {
    "Date": "date",
    "HomeTeam": "hometeam",
    "AwayTeam": "awayteam",
    "FTHG": "fthg",
    "FTAG": "ftag",
    "FTR": "ftr",
    "HTHG": "hthg",
    "HTAG": "htag",
    "HTR": "htr",
    "HS": "home_shots",
    "AS": "away_shots",
    "HST": "home_shots_on_target",
    "AST": "away_shots_on_target",
    "HC": "home_corners",
    "AC": "away_corners",
    "HY": "home_yellow",
    "AY": "away_yellow",
    "HR": "home_red",
    "AR": "away_red",
    "B365H": "b365h",
    "B365D": "b365d",
    "B365A": "b365a",
    "BWH": "bwh",
    "BWD": "bwd",
    "BWA": "bwa",
    "PSH": "psh",
    "PSD": "psd",
    "PSA": "psa",
    "PSCH": "psch",
    "PSCD": "pscd",
    "PSCA": "psca",
}

common_cols = list(col_map.keys())

def import_csv(year, league):
    url = base_url.format(year, league)
    try:
        r = requests.get(url, timeout=10)
        if r.status_code != 200 or len(r.text) < 100:
            print(f"⚠️ Skip {year}_{league} (vuoto o non valido)")
            return
        df = pd.read_csv(StringIO(r.text), usecols=lambda c: c in common_cols)

        if df.empty:
            print(f"⚠️ Skip {year}_{league} (nessun dato)")
            return

        # rinomina colonne
        df = df.rename(columns=col_map)

        # parsing date
        df["date"] = pd.to_datetime(df["date"], errors="coerce", dayfirst=True)

        # inserisci in Postgres
        with engine.begin() as conn:
            for _, row in df.iterrows():
                placeholders = ", ".join([f":{col}" for col in df.columns])
                columns = ", ".join(df.columns)
                sql = text(f"""
                    INSERT INTO matches ({columns})
                    VALUES ({placeholders})
                    ON CONFLICT (date, hometeam, awayteam) DO NOTHING;
                """)
                conn.execute(sql, row.to_dict())

        print(f"✅ Importato {year}_{league} ({len(df)} partite)")

    except Exception as e:
        print(f"❌ Errore {year}_{league}: {e}")

def main():
    for year in years:
        for league in leagues:
            import_csv(year, league)

if __name__ == "__main__":
    main()
