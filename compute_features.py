import pandas as pd
from sqlalchemy import create_engine, text
import logging
from typing import Dict, List, Tuple
import numpy as np

# Configurazione logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Connessione a Postgres (stesse credenziali di import_matches.py)
DATABASE_URL = "postgresql://postgres:Vasco!31@localhost:5432/bet"
engine = create_engine(DATABASE_URL)

def get_all_matches() -> pd.DataFrame:
    """Recupera tutte le partite dal database"""
    query = """
    SELECT id, season, league, date, hometeam, awayteam,
           fthg, ftag, ftr, hthg, htag, htr
    FROM matches
    ORDER BY season, league, date
    """
    with engine.connect() as conn:
        df = pd.read_sql(query, conn)
    return df

def calculate_matchday(df: pd.DataFrame) -> pd.Series:
    """Calcola il numero di giornata per ogni partita (season + league)"""
    df = df.copy()
    df['giornata'] = df.groupby(['season', 'league']).cumcount() + 1
    return df['giornata']

def calculate_cumulative_stats(df: pd.DataFrame) -> pd.DataFrame:
    """Calcola statistiche cumulative per ogni squadra"""
    df = df.copy()

    # Prepara i dati per il calcolo delle statistiche cumulative
    home_stats = []
    away_stats = []

    for _, group in df.groupby(['season', 'league']):
        group = group.sort_values('date')

        # Calcola statistiche cumulative per squadre di casa
        for team in group['hometeam'].unique():
            team_home_matches = group[group['hometeam'] == team].copy()
            team_home_matches['cumulative_gf_home'] = team_home_matches['fthg'].cumsum().shift(1).fillna(0)
            team_home_matches['cumulative_gs_home'] = team_home_matches['ftag'].cumsum().shift(1).fillna(0)
            team_home_matches['cumulative_points_home'] = team_home_matches['ftr'].apply(
                lambda x: 3 if x == 'H' else (1 if x == 'D' else 0)
            ).cumsum().shift(1).fillna(0)

            home_stats.append(team_home_matches[['id', 'cumulative_gf_home', 'cumulative_gs_home', 'cumulative_points_home']])

        # Calcola statistiche cumulative per squadre in trasferta
        for team in group['awayteam'].unique():
            team_away_matches = group[group['awayteam'] == team].copy()
            team_away_matches['cumulative_gf_away'] = team_away_matches['ftag'].cumsum().shift(1).fillna(0)
            team_away_matches['cumulative_gs_away'] = team_away_matches['fthg'].cumsum().shift(1).fillna(0)
            team_away_matches['cumulative_points_away'] = team_away_matches['ftr'].apply(
                lambda x: 3 if x == 'A' else (1 if x == 'D' else 0)
            ).cumsum().shift(1).fillna(0)

            away_stats.append(team_away_matches[['id', 'cumulative_gf_away', 'cumulative_gs_away', 'cumulative_points_away']])

    # Unisci le statistiche
    home_df = pd.concat(home_stats) if home_stats else pd.DataFrame()
    away_df = pd.concat(away_stats) if away_stats else pd.DataFrame()

    # Merge con il DataFrame originale
    result_df = df.copy()
    if not home_df.empty:
        result_df = result_df.merge(home_df, on='id', how='left')
    if not away_df.empty:
        result_df = result_df.merge(away_df, on='id', how='left')

    return result_df

def calculate_form(df: pd.DataFrame, window: int = 5) -> pd.DataFrame:
    """Calcola la forma (media punti) nelle ultime N partite"""
    df = df.copy()

    form_stats = []

    for (season, league), group in df.groupby(['season', 'league']):
        group = group.sort_values('date')

        # Calcola forma per squadre di casa
        for team in group['hometeam'].unique():
            team_matches = group[(group['hometeam'] == team) | (group['awayteam'] == team)].copy()
            team_matches['points'] = team_matches.apply(
                lambda row: 3 if (row['hometeam'] == team and row['ftr'] == 'H') or
                                (row['awayteam'] == team and row['ftr'] == 'A')
                            else (1 if row['ftr'] == 'D' else 0),
                axis=1
            )

            team_matches[f'form_last{window}'] = team_matches['points'].rolling(window=window, min_periods=1).mean().shift(1)
            form_stats.append(team_matches[['id', f'form_last{window}']])

    # Unisci le statistiche di forma
    form_df = pd.concat(form_stats) if form_stats else pd.DataFrame()
    result_df = df.copy()

    if not form_df.empty:
        # Separa forma home e away
        home_form = form_df.rename(columns={f'form_last{window}': f'form_home_last{window}'})
        away_form = form_df.rename(columns={f'form_last{window}': f'form_away_last{window}'})

        result_df = result_df.merge(home_form, on='id', how='left')
        result_df = result_df.merge(away_form, on='id', how='left')

    return result_df

def calculate_promotion_status(df: pd.DataFrame) -> pd.DataFrame:
    """Calcola lo status di promozione/retrocessione"""
    df = df.copy()
    df['status_home'] = 0
    df['status_away'] = 0

    # Per la prima implementazione, impostiamo tutto a 0 (stessa lega)
    # Questa funzione può essere estesa in futuro con dati storici
    return df

def calculate_all_features(df: pd.DataFrame) -> pd.DataFrame:
    """Calcola tutte le feature per le partite"""
    logger.info("Calcolo giornate...")
    df['giornata'] = calculate_matchday(df)

    logger.info("Calcolo statistiche cumulative...")
    df = calculate_cumulative_stats(df)

    logger.info("Calcolo forma ultime 3 partite...")
    df = calculate_form(df, window=3)

    logger.info("Calcolo forma ultime 5 partite...")
    df = calculate_form(df, window=5)

    logger.info("Calcolo status promozione/retrocessione...")
    df = calculate_promotion_status(df)

    # Calcola differenze gol
    df['diff_gf'] = df['cumulative_gf_home'] - df['cumulative_gf_away']
    df['diff_gs'] = df['cumulative_gs_home'] - df['cumulative_gs_away']

    return df

def insert_features_to_db(features_df: pd.DataFrame):
    """Inserisce le feature calcolate nel database"""
    if features_df.empty:
        logger.warning("Nessuna feature da inserire")
        return

    # Prepara i dati per l'inserimento
    features_to_insert = features_df[[
        'id', 'season', 'league', 'giornata', 'cumulative_points_home', 'cumulative_points_away',
        'cumulative_gf_home', 'cumulative_gs_home', 'cumulative_gf_away', 'cumulative_gs_away',
        'diff_gf', 'diff_gs', 'form_home_last3', 'form_away_last3',
        'form_home_last5', 'form_away_last5', 'status_home', 'status_away'
    ]].copy()

    # Rinomina le colonne per matchare il database
    features_to_insert = features_to_insert.rename(columns={
        'id': 'match_id',
        'cumulative_points_home': 'points_home',
        'cumulative_points_away': 'points_away',
        'cumulative_gf_home': 'gf_home_total',
        'cumulative_gs_home': 'gs_home_total',
        'cumulative_gf_away': 'gf_away_total',
        'cumulative_gs_away': 'gs_away_total'
    })

    # Inserisci nel database
    with engine.begin() as conn:
        for _, row in features_to_insert.iterrows():
            placeholders = ", ".join([f":{col}" for col in features_to_insert.columns])
            columns = ", ".join(features_to_insert.columns)

            sql = text(f"""
                INSERT INTO features_matches ({columns})
                VALUES ({placeholders})
                ON CONFLICT (match_id) DO UPDATE SET
                    season = EXCLUDED.season,
                    league = EXCLUDED.league,
                    giornata = EXCLUDED.giornata,
                    points_home = EXCLUDED.points_home,
                    points_away = EXCLUDED.points_away,
                    gf_home_total = EXCLUDED.gf_home_total,
                    gs_home_total = EXCLUDED.gs_home_total,
                    gf_away_total = EXCLUDED.gf_away_total,
                    gs_away_total = EXCLUDED.gs_away_total,
                    diff_gf = EXCLUDED.diff_gf,
                    diff_gs = EXCLUDED.diff_gs,
                    form_home_last3 = EXCLUDED.form_home_last3,
                    form_away_last3 = EXCLUDED.form_away_last3,
                    form_home_last5 = EXCLUDED.form_home_last5,
                    form_away_last5 = EXCLUDED.form_away_last5,
                    status_home = EXCLUDED.status_home,
                    status_away = EXCLUDED.status_away;
            """)

            conn.execute(sql, row.to_dict())

    logger.info(f"✅ Inserite/aggiornate {len(features_to_insert)} righe in features_matches")

def main():
    """Funzione principale"""
    try:
        logger.info("Recupero partite dal database...")
        matches_df = get_all_matches()

        if matches_df.empty:
            logger.warning("Nessuna partita trovata nel database")
            return

        logger.info(f"Trovate {len(matches_df)} partite")

        # Calcola le feature per ogni season e league
        total_processed = 0

        for (season, league), group in matches_df.groupby(['season', 'league']):
            logger.info(f"Elaborazione stagione {season}_{league} ({len(group)} partite)")

            features_df = calculate_all_features(group)
            insert_features_to_db(features_df)

            total_processed += len(group)
            logger.info(f"✅ Calcolate feature stagione {season}_{league} ({len(group)} match)")

        logger.info(f"🎯 Operazione completata! Elaborate {total_processed} partite totali")

    except Exception as e:
        logger.error(f"❌ Errore durante il calcolo delle feature: {e}")
        raise

if __name__ == "__main__":
    main()
