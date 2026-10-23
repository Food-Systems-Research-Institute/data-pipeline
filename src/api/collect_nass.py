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
def getParams(param_url: str, param: str) -> list[str]:
    param_params = {"key": API_KEY, "param": param}

    param_response = requests.get(param_url, params=param_params, timeout=60)

    print("Status code:", param_response.status_code)
    print("Response preview:", param_response.text[:1000])

    return param_response.json()[param]


def build_request_and_get_record_count(
    sector: str, **kwargs: str | int
) -> tuple[int, Params, str]:
    params: Params = {
        "key": API_KEY,
        "format": "JSON",
        "source_desc": "CENSUS",
        "sector_desc": sector,
    }

    table_parts = [sector]

    for key, value in kwargs.items():
        params[key] = value
        table_parts.append(str(value))

    response = requests.get(count_url, params=params, timeout=60)

    table_name = "_".join(table_parts).replace(" ", "_").lower()

    return int(response.json()["count"]), params, table_name


# Get raw data from NASS API based on the specified parameters
def get_NASS_data(
    get_url: str, row_count: int, params: Params, table_name: str
) -> pd.DataFrame | None:
    if row_count > 50000:
        print(f"Request too large ({row_count} rows), try further filtering")
        return None
    
    response = requests.get(get_url, params=params, timeout=60)
    print("Status code:", response.status_code)

    if response.status_code != 200:
        print(f"Request failed for {table_name}: {response.text[:500]}")
        return pd.DataFrame()

    raw_data = response.json()

    if "data" not in raw_data:
        print(f"No data field for {table_name}: {raw_data}")
        return pd.DataFrame()

    return pd.DataFrame(raw_data["data"])


def build_NASS_table(
    get_url: str, params: Params, table_name: str, row_count: int
) -> None:
    raw_data = get_NASS_data(get_url, row_count, params, table_name)

    if raw_data is None:
        print("build table failed, request was too large")
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

    for year in [2002, 2007, 2012, 2017, 2022]:
        for state in northeast_states:
            count, params, table_name = build_request_and_get_record_count(
                sector="ECONOMICS", year=year, agg_level_desc="STATE", state_name=state
            )
            build_NASS_table(get_url, params, table_name, count)
            time.sleep(1)
