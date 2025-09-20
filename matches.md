# Tabella `matches`

Questa tabella contiene i dati delle partite importate dai CSV di football-data.co.uk.
Ogni riga rappresenta una singola partita.

## Struttura delle colonne

| Colonna                | Tipo              | Nullabile | Descrizione                                                                 |
|-------------------------|-------------------|-----------|-----------------------------------------------------------------------------|
| `id`                   | integer (PK)      | NO        | Identificatore univoco della partita (Primary Key, autoincrement)           |
| `date`                 | date              | NO        | Data della partita (formato dd/mm/yy)                                       |
| `hometeam`             | text              | NO        | Squadra di casa                                                             |
| `awayteam`             | text              | NO        | Squadra in trasferta                                                        |
| `fthg`                 | integer           | Sì        | Full Time Home Goals = gol casa a fine partita                              |
| `ftag`                 | integer           | Sì        | Full Time Away Goals = gol trasferta a fine partita                         |
| `ftr`                  | text              | Sì        | Full Time Result (H = casa, D = pareggio, A = trasferta)                    |
| `hthg`                 | integer           | Sì        | Half Time Home Goals                                                        |
| `htag`                 | integer           | Sì        | Half Time Away Goals                                                        |
| `htr`                  | text              | Sì        | Half Time Result (H/D/A)                                                    |
| `home_shots`           | double precision  | Sì        | Tiri totali squadra di casa                                                 |
| `away_shots`           | double precision  | Sì        | Tiri totali squadra in trasferta                                            |
| `home_shots_on_target` | double precision  | Sì        | Tiri in porta squadra di casa                                               |
| `away_shots_on_target` | double precision  | Sì        | Tiri in porta squadra in trasferta                                          |
| `home_corners`         | double precision  | Sì        | Calci d’angolo squadra di casa                                              |
| `away_corners`         | double precision  | Sì        | Calci d’angolo squadra in trasferta                                         |
| `home_yellow`          | double precision  | Sì        | Ammonizioni squadra di casa                                                 |
| `away_yellow`          | double precision  | Sì        | Ammonizioni squadra in trasferta                                            |
| `home_red`             | double precision  | Sì        | Espulsioni squadra di casa                                                  |
| `away_red`             | double precision  | Sì        | Espulsioni squadra in trasferta                                             |
| `b365h`                | double precision  | Sì        | Bet365 home win odds                                                        |
| `b365d`                | double precision  | Sì        | Bet365 draw odds                                                            |
| `b365a`                | double precision  | Sì        | Bet365 away win odds                                                        |
| `bwh`                  | double precision  | Sì        | Bet&Win home win odds                                                       |
| `bwd`                  | double precision  | Sì        | Bet&Win draw odds                                                           |
| `bwa`                  | double precision  | Sì        | Bet&Win away win odds                                                       |
| `psh`                  | double precision  | Sì        | Pinnacle home win odds                                                      |
| `psd`                  | double precision  | Sì        | Pinnacle draw odds                                                          |
| `psa`                  | double precision  | Sì        | Pinnacle away win odds                                                      |
| `psch`                 | double precision  | Sì        | Pinnacle closing home win odds                                              |
| `pscd`                 | double precision  | Sì        | Pinnacle closing draw odds                                                  |
| `psca`                 | double precision  | Sì        | Pinnacle closing away win odds                                              |
| `season`               | text              | NO        | Stagione sportiva (es. 2425)                                                |
| `league`               | text              | NO        | Campionato/lega (es. E0 = Premier League, I1 = Serie A, ecc.)               |

## Vincoli

- **Primary Key**: `id`
- **Unique Constraint**: `(season, league, date, hometeam, awayteam)`
