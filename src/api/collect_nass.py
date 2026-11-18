# NASS API Data Collection Script
import os
import re
import time
from pathlib import Path

import duckdb as db
import pandas as pd
import requests
from dotenv import load_dotenv

from utils import find_project_root

PROJECT_DIR = find_project_root()
load_dotenv(PROJECT_DIR / ".env")
API_KEY = os.getenv("NASS_API_KEY")
DB_PATH = PROJECT_DIR / "agData.duckdb"

if API_KEY is None:
    print("API key not found")
else:
    print("API key loaded successfully")

param_url = "https://quickstats.nass.usda.gov/api/get_param_values/"
get_url = "https://quickstats.nass.usda.gov/api/api_GET/"
count_url = "https://quickstats.nass.usda.gov/api/get_counts/"

# Set Params as class to pass as type hints throughout functions
Params = dict[str, str | int | None]


# gets the categories for the descriptive parameters as a list
#useful if unable to access usda website
# (ex. param is sector_desc, output is ['ANIMALS & PRODUCTS', 'CROPS', 'DEMOGRAPHICS', 'ECONOMICS', 'ENVIRONMENTAL'])
def get_params(param_url: str, key_word: str) -> list[str]:
    param_params = {"key": API_KEY, "param": key_word}

    param_response = requests.get(param_url, params=param_params, timeout=60)

    print("Status code:", param_response.status_code)
    print("Response preview:", param_response.text[:1000])

    return param_response.json()[key_word]


def build_request(source: str, sector: str, **kwargs: str | int) -> Params:
    params: Params = {
        "key": API_KEY,
        "format": "JSON",
        "source_desc": source,
        "sector_desc": sector,
    }

    for key, value in kwargs.items():
        params[key] = value

    return params


def get_record_count(count_url, params: dict) -> int:
    response = requests.get(count_url, params=params, timeout=60)

    return int(response.json()["count"])


def get_table_name(params: dict) -> str:
    parts = [
        params["source_desc"],
        params["sector_desc"],
        params.get("year"),
        params.get("state_name"),
    ]
    skip = {"key", "format", "source_desc", "sector_desc", "year", "state_name"}

    for k in sorted(params):
        if k in skip:
            continue
        if k == "agg_level_desc" and params[k] == "STATE":
            continue
        parts.append(params[k])

    table_pieces = []
    for p in parts:
        if p not in (None, ""):
            table_pieces.append(str(p))

    table_name = ("_").join(table_pieces)

    return re.sub(r"\W+", "_", table_name).strip("_").lower()


# Get raw data from NASS API based on the specified parameters
def get_NASS_data(
    get_url: str, params: Params, table_name: str
) -> pd.DataFrame | None:


    response = requests.get(get_url, params=params, timeout=60)
    print("Status code:", response.status_code)

    if response.status_code == 413:
        print(f"TOO LARGE: {table_name}, split by group_desc")
        return None

    if response.status_code != 200:
        print(f"Request failed for {table_name}: {response.text[:500]}")
        return None

    raw_data = response.json()

    if "data" not in raw_data:
        print(f"No data field for {table_name}: {raw_data}")
        return None

    return pd.DataFrame(raw_data["data"])


def build_NASS_table(
    get_url: str, params: Params, table_name: str) -> None:
    raw_data = get_NASS_data(get_url, params, table_name)

    if raw_data is None:
        print("build table failed, request was too large or invalid request")
        return

    conn = db.connect(DB_PATH)
    conn.execute("""
            CREATE SCHEMA IF NOT EXISTS raw_nass
            """)

    conn.execute(f"""
        CREATE OR REPLACE TABLE raw_nass.{table_name} AS
        SELECT * FROM raw_data
        """)

    print(f"Loaded {len(raw_data)} rows into raw_nass.{table_name}")

    conn.close()


def combine_nass_tables(
    years: list,
    source_schema: str = "raw_nass",
    target: str = "raw_nass_combined.nass_all",
    name_prefix: str = "",
    drop_sources: bool = False
) -> None:
    
    conn = db.connect(DB_PATH)

    target_schema = target.split(".")[0]
    conn.execute(f"CREATE SCHEMA IF NOT EXISTS {target_schema}")

    tables = conn.execute(
        """
        SELECT table_name
        FROM duckdb_tables()
        WHERE schema_name = ? AND table_name LIKE ?
        ORDER BY table_name
        """,
        [source_schema, f"{name_prefix}%"],
    ).fetchall()
    tables = [t[0] for t in tables]

    if not tables:
        conn.close()
        raise RuntimeError(f"No tables found in {source_schema}")

    selects = [
        f"SELECT *, '{t}' AS source_table FROM {source_schema}.\"{t}\"" for t in tables
    ]
    query = "\nUNION ALL BY NAME\n".join(selects)

    start = str(years[0])

    end = str(years[-1])

    target = target + f"_{start}_" + end

    conn.execute(f"CREATE OR REPLACE TABLE {target} AS\n{query}")

    result = conn.execute(f"SELECT COUNT(*) FROM {target}").fetchone()

    if result is not None:
        n = result[0]
    else:
        n = 0

    print(f"Combined {len(tables)} tables into {target}: {n:,} rows")

    if drop_sources:
        for t in tables:
            conn.execute(f'DROP TABLE {source_schema}."{t}"')
        print(f"Dropped {len(tables)} source tables")

    conn.close()


SECTORS = ['ANIMALS & PRODUCTS', 
           'CROPS', 
           'DEMOGRAPHICS', 
           'ECONOMICS', 
           'ENVIRONMENTAL'
           ]

NORTHEAST = [
    "CONNECTICUT",
    "MASSACHUSETTS",
    "NEW HAMPSHIRE",
    "VERMONT",
    "MAINE",
    "NEW YORK",
    "PENNSYLVANIA",
    "NEW JERSEY",
    "RHODE ISLAND",
    ]

def collect_nass(years, 
                 source = "CENSUS", 
                 sectors = SECTORS, 
                 states = NORTHEAST, 
                 dry_run=True, 
                 combine_tables=False,
                 drop_sources=False,
                 **filters) -> None:
    
    filters.setdefault("agg_level_desc", "STATE")
    for sector in sectors:
        for year in years:
            for state in states:
                try:
                    params = build_request(
                        source, sector, year=year, state_name=state, **filters
                    )
                    
                    table_name = get_table_name(params)

                    if dry_run:
                        count = get_record_count(count_url, params)

                        if count == 0:
                            print(f"no data: {sector} {state} {year}")
                            continue
                        if count > 50000:
                            print(f"TOO LARGE ({count}): {sector} {state} {year}")
                            continue
                        print(f"OK ({count}): {sector} {state} {year}")
                    else:
                        build_NASS_table(get_url, params, table_name)
                except (requests.RequestException, 
                        requests.JSONDecodeError,
                        KeyError, 
                        ValueError, 
                        db.Error) as e:
                        print(f"FAILED {sector} {state} {year}: {type(e).__name__}: {e}")
                time.sleep(2)
    if combine_tables:
        combine_nass_tables(years,
                            source_schema = "raw_nass",
                            target = "raw_nass_combined.nass_all",
                            name_prefix = "",
                            drop_sources = drop_sources)


SECTORS = ['ANIMALS & PRODUCTS', 
           'CROPS', 
           'DEMOGRAPHICS', 
           'ECONOMICS', 
           'ENVIRONMENTAL'
           ]

NORTHEAST = [
    "CONNECTICUT",
    "MASSACHUSETTS",
    "NEW HAMPSHIRE",
    "VERMONT",
    "MAINE",
    "NEW YORK",
    "PENNSYLVANIA",
    "NEW JERSEY",
    "RHODE ISLAND",
    ]


if __name__ == "__main__":
    # UNCOMMENT BELOW TO COLLECT ALL NASS CENSUS DATA
    '''
    collect_nass("CENSUS", 
                 years=[1997, 2002, 2007, 2012, 2017, 2022], 
                 sectors=SECTORS, 
                 states=NORTHEAST, 
                 dry_run=False, 
                 combine_tables=True, 
                 drop_sources=True)
    '''
    collect_nass(years=[2017, 2022], source = "CENSUS", sectors=["CROPS"], states=NORTHEAST, dry_run=False, combine_tables=True, drop_sources=True)

    #get_params(param_url, key_word="group_desc")
