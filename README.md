# Mat-prosjekt Databricks

Dette prosjektet henter matvaredata fra norske matbutikker og lager tabeller som kan brukes til analyse av pris, næringsinnhold og sammenligning mellom varer.

Prosjektet er laget for Databricks. Data hentes fra butikk-API-er, lagres som JSON i Azure Blob Storage, leses inn i Databricks og bygges videre til Delta-tabeller i bronze-, silver- og gold-lag.

## Hva prosjektet gjør

1. Henter produkter fra SPAR og MENY.
2. Lagrer rådata som JSON i Azure Blob Storage.
3. Leser JSON-filen inn i en enkel `products`-tabell.
4. Lager en bronze-tabell med relevante felter hentet ut fra JSON.
5. Lager en silver-tabell med ryddigere kolonnenavn og numeriske datatyper.
6. Lager en gold-tabell med ferdige lenker, standardverdier og beregnede næringsverdier per krone.

## Prosjektstruktur

```text
.
├── weekly_scrape_job.py      # Oppretter en ukentlig Databricks-jobb
├── .env                      # Miljøverdier for prosjektet
├── .env_example              # Eksempel på hvilke miljøverdier som må fylles inn
├── src/
│   ├── config.py             # Leser .env og gjør verdiene tilgjengelige i Python
│   ├── scrape.py             # Henter produktdata og lagrer JSON i Azure Blob Storage
│   └── products.py           # Leser JSON fra Azure Blob Storage og lager products-tabellen
├── sql/
│   ├── bronze.sql            # Lager bronze-tabell fra products
│   ├── silver.sql            # Lager silver-tabell fra bronze
│   └── gold.sql              # Lager gold-tabell fra silver
└── experiments/
    ├── inspect_json.ipynb    # Notebook for å undersøke JSON-data
    ├── inspect_tables.ipynb  # Notebook for å undersøke tabeller
    └── blob_connection_test.py
```

## Dataflyt

```text
SPAR / MENY
    ↓
src/scrape.py
    ↓
Azure Blob Storage JSON
    ↓
src/products.py
    ↓
products
    ↓
sql/bronze.sql
    ↓
product_nutritiens_bronze
    ↓
sql/silver.sql
    ↓
product_nutritiens_silver
    ↓
sql/gold.sql
    ↓
product_nutritiens_gold
```

## Tabeller

### `products`

En enkel råtabell med:

- `chain`: butikkjede, for eksempel `spar` eller `meny`
- `product_json`: hele produktobjektet lagret som JSON-tekst

### `product_nutritiens_bronze`

Bronze-tabellen henter ut felter fra `product_json`, blant annet:

- produktnavn
- merkevare
- pris
- sammenligningspris
- EAN
- næringsinnhold

Denne tabellen holder verdiene tett på rådataene.

### `product_nutritiens_silver`

Silver-tabellen rydder opp i bronze-dataene:

- fjerner rader uten komplett næringsinnhold
- konverterer tallverdier til `DOUBLE`
- gir noen kolonner mer standardiserte navn
- fjerner felter som ikke brukes videre

### `product_nutritiens_gold`

Gold-tabellen er laget for analyse og visning:

- lager full produktlenke til SPAR eller MENY
- lager full bildelenke
- erstatter manglende merkevare og beskrivelse med standardtekst
- beregner næringsverdier per pakke
- beregner næringsverdier per krone

## Databricks-jobb

`weekly_scrape_job.py` oppretter en Databricks-jobb som kjører hver mandag kl. 03:00 i tidssonen `Europe/Oslo`.

Jobben kjører oppgavene i denne rekkefølgen:

1. `scrape`
2. `scraped_json_to_sql_table`
3. `bronze`
4. `silver`
5. `gold`

Før jobben brukes må disse verdiene settes i `.env`:

- `USER_EMAIL`
- `WAREHOUSE_ID`

Prosjektet forventer også en Databricks Service Credential med navnet `customer_support_blob`, som brukes for tilgang til Azure Blob Storage.

## Miljøvariabler

Prosjektet leser miljøverdier fra `.env` via `src/config.py`. Dette gjør at spesifikke verdier kan endres uten å endre selve koden.

Bruk `.env_example` som mal når prosjektet settes opp i et nytt miljø.

## Azure Blob Storage

Rådata lagres i stien som settes av `.env`:

```text
${AZURE_STORAGE_ACCOUNT_URL}/${AZURE_STORAGE_CONTAINER}/${AZURE_BLOB_PREFIX}/
```

Filnavnene får tidsstempel, for eksempel:

```text
weekly_data_YYYYMMDDTHHMMSSZ.json
```

## Merknader

- Prosjektet bruker foreløpig SPAR og MENY.
- `src/products.py` peker på én konkret JSON-fil via `PRODUCTS_BLOB_NAME` i `.env`. Hvis en ny scrape-fil skal brukes, må denne verdien oppdateres.
- Tabellnavnet `product_nutritiens_*` ser ut til å være brukt konsekvent i SQL-filene.
