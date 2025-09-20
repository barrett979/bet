# Tabella: features_matches

Questa tabella contiene le feature calcolate per ogni partita, utili per modelli di previsione (es. XGBoost).

| Colonna           | Tipo    | Nullabile | Default                                      | Descrizione                                                                 |
|-------------------|---------|-----------|----------------------------------------------|-----------------------------------------------------------------------------|
| id                | integer | NOT NULL  | nextval('features_matches_id_seq'::regclass) | Identificativo univoco della riga (PK)                                      |
| match_id          | integer | NOT NULL  |                                              | Riferimento alla partita nella tabella `matches`                            |
| season            | text    | NOT NULL  |                                              | Stagione di riferimento (es. 1819, 1920, …)                                |
| league            | text    | NOT NULL  |                                              | Codice lega/campionato (es. E0=Premier League, I1=Serie A, SP1=La Liga…)   |
| giornata          | integer | YES       |                                              | Numero della giornata (incrementale per lega+stagione, ordinato per data)   |
| points_home       | integer | YES       |                                              | Punti cumulati squadra di casa fino alla partita (esclusa)                  |
| points_away       | integer | YES       |                                              | Punti cumulati squadra trasferta fino alla partita (esclusa)                |
| gf_home_total     | integer | YES       |                                              | Gol fatti totali squadra di casa (casa+trasferta, cumulati precedenti)      |
| gs_home_total     | integer | YES       |                                              | Gol subiti totali squadra di casa (casa+trasferta, cumulati precedenti)     |
| gf_away_total     | integer | YES       |                                              | Gol fatti totali squadra trasferta (casa+trasferta, cumulati precedenti)    |
| gs_away_total     | integer | YES       |                                              | Gol subiti totali squadra trasferta (casa+trasferta, cumulati precedenti)   |
| gf_home_at_home   | integer | YES       |                                              | Gol fatti squadra di casa **solo** nelle partite casalinghe precedenti      |
| gs_home_at_home   | integer | YES       |                                              | Gol subiti squadra di casa **solo** nelle partite casalinghe precedenti     |
| gf_away_when_away | integer | YES       |                                              | Gol fatti squadra trasferta **solo** nelle partite in trasferta precedenti  |
| gs_away_when_away | integer | YES       |                                              | Gol subiti squadra trasferta **solo** nelle partite in trasferta precedenti |
| diff_gf           | integer | YES       |                                              | Differenza gol fatti cumulati (casa - trasferta) fino alla partita          |
| diff_gs           | integer | YES       |                                              | Differenza gol subiti cumulati (casa - trasferta) fino alla partita         |
| form_home_last3   | real    | YES       |                                              | Media punti squadra di casa nelle ultime 3 partite (casa+trasferta)         |
| form_away_last3   | real    | YES       |                                              | Media punti squadra trasferta nelle ultime 3 partite (casa+trasferta)       |
| form_home_last5   | real    | YES       |                                              | Media punti squadra di casa nelle ultime 5 partite (casa+trasferta)         |
| form_away_last5   | real    | YES       |                                              | Media punti squadra trasferta nelle ultime 5 partite (casa+trasferta)       |
| status_home       | integer | YES       |                                              | Stato squadra di casa: 0=stessa lega, +1=retrocesso, -1=promosso            |
| status_away       | integer | YES       |                                              | Stato squadra trasferta: 0=stessa lega, +1=retrocesso, -1=promosso          |

### Indici e Chiavi
- **PK**: `id`
- **FK**: `match_id` → `matches(id)` (ON DELETE CASCADE)
