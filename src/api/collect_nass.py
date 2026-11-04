# NASS API Data Collection Script
import os
import time

import duckdb as db
import pandas as pd
import requests
from dotenv import load_dotenv

from utils import find_project_root

PROJECT_DIR = find_project_root()
load_dotenv(PROJECT_DIR / ".env")
API_KEY = os.getenv("NASS_API_KEY")

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
# (ex. param is source_desc, output is ['ANIMALS & PRODUCTS', 'CROPS', 'DEMOGRAPHICS', 'ECONOMICS', 'ENVIRONMENTAL'])
def getParams(param_url: str, key_word: str) -> list[str]:
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
    return "_".join(str(p) for p in parts if p).replace(" ", "_").lower()
        


# Get raw data from NASS API based on the specified parameters
def get_NASS_data(
    get_url: str, row_count: int, params: Params, table_name: str
) -> pd.DataFrame | None:
    if row_count > 50000:
        raise ValueError(f"Request too large ({row_count} rows), try further filtering")

    
    response = requests.get(get_url, params=params, timeout=60)
    print("Status code:", response.status_code)

    if response.status_code != 200:
        print(f"Request failed for {table_name}: {response.text[:500]}")
        return None

    raw_data = response.json()

    if "data" not in raw_data:
        print(f"No data field for {table_name}: {raw_data}")
        return None

    return pd.DataFrame(raw_data["data"])


def build_NASS_table(
    get_url: str, params: Params, table_name: str, row_count: int
) -> None:
    raw_data = get_NASS_data(get_url, row_count, params, table_name)


    if raw_data is None:
        print("build table failed, request was too large or invalid request")
        return

    conn = db.connect("agData.duckdb")
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
    source_schema: str = "raw_nass",
    target: str = "raw_nass_combined.nass_all",
    name_prefix: str = "",
    drop_sources: bool = False,
    db_path: str = "agData.duckdb",
) -> None:
    conn = db.connect(db_path)

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
        f"SELECT *, '{t}' AS source_table FROM {source_schema}.\"{t}\""
        for t in tables
    ]
    query = "\nUNION ALL BY NAME\n".join(selects)

    conn.execute(f"CREATE OR REPLACE TABLE {target} AS\n{query}")

    n = conn.execute(f"SELECT COUNT(*) FROM {target}").fetchone()[0]
    print(f"Combined {len(tables)} tables into {target}: {n:,} rows")

    if drop_sources:
        for t in tables:
            conn.execute(f'DROP TABLE {source_schema}."{t}"')
        print(f"Dropped {len(tables)} source tables")

    conn.close()


if __name__ == "__main__":


    northeast_states = [
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

    for year in range(1997, 2025 + 1):
        for state in northeast_states:
            params = build_request(
                                source="CENSUS",
                                sector="ECONOMICS", 
                                year=year, 
                                agg_level_desc="STATE", 
                                state_name=state
                            )
            count = get_record_count(count_url, params)
            table_name = get_table_name(params)
            
            build_NASS_table(get_url, params, table_name, count)
            time.sleep(.5)

    #combine_nass_tables(name_prefix="census_economics")