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
<<<<<<< HEAD

# Set Params as class to pass as type hints throughout functions
Params = dict[str, str | int | None]
=======
>>>>>>> 0c07d63c320ba1d3fa6c74c14a0f510031d88d66


# gets the categories for the descriptive parameters as a list
# (ex. param is source_desc, output is ['ANIMALS & PRODUCTS', 'CROPS', 'DEMOGRAPHICS', 'ECONOMICS', 'ENVIRONMENTAL'])
def getParams(param_url: str, key_word: str) -> list[str]:
    param_params = {"key": API_KEY, "param": key_word}

    param_response = requests.get(param_url, params=param_params, timeout=60)

    print("Status code:", param_response.status_code)
    print("Response preview:", param_response.text[:1000])

    return param_response.json()[key_word]


<<<<<<< HEAD
def build_request(sector: str, **kwargs: str | int) -> Params:
    params: Params = {
            "key": API_KEY,
            "format": "JSON",
            "source_desc": "CENSUS",
            "sector_desc": sector,
            }
=======
def build_request_and_get_record_count(sector, **kwargs):
    params = {
        "key": API_KEY,
        "format": "JSON",
        "source_desc": "CENSUS",
        "sector_desc": sector,
    }
>>>>>>> 0c07d63c320ba1d3fa6c74c14a0f510031d88d66

    for key, value in kwargs.items():
            params[key] = value

<<<<<<< HEAD
    return params
=======
    response = requests.get(count_url, params=params, timeout=60)
>>>>>>> 0c07d63c320ba1d3fa6c74c14a0f510031d88d66


def get_record_count(params: dict) -> int:
    response = requests.get(count_url, params=params, timeout=60)

    return int(response.json()["count"])
    

def get_table_name(parmas: dict) -> str:
    table_parts = list(str(params.values()))[2:]
    
    table_name = "_".join(table_parts).replace(" ", "_").lower()
    
    return table_name
        


# Get raw data from NASS API based on the specified parameters
def get_NASS_data(
    get_url: str, row_count: int, params: Params, table_name: str
) -> pd.DataFrame | None:
    if row_count > 50000:
<<<<<<< HEAD
        print(f"Request too large ({row_count} rows), try further filtering")
        return None
    
=======
        raise ValueError(f"Request too large ({row_count} rows), try further filtering")

>>>>>>> 0c07d63c320ba1d3fa6c74c14a0f510031d88d66
    response = requests.get(get_url, params=params, timeout=60)
    print("Status code:", response.status_code)

    if response.status_code != 200:
        print(f"Request failed for {table_name}: {response.text[:500]}")
        return pd.DataFrame()

    raw_data = response.json()

    if "data" not in raw_data:
        raise ValueError(f"No data field in response: {raw_data}")

    return pd.DataFrame(raw_data["data"])


<<<<<<< HEAD
def build_NASS_table(
    get_url: str, params: Params, table_name: str, row_count: int
) -> None:
    raw_data = get_NASS_data(get_url, row_count, params, table_name)

    sector = params["sector_desc"]

    if raw_data is None:
        print("build table failed, request was too large")
        return
=======
def build_NASS_table(get_url, params, table_name, row_count):
    raw_data = get_NASS_data(get_url, row_count, params)

    if raw_data is None:
        print("build table failed, request was too large")
        return None
>>>>>>> 0c07d63c320ba1d3fa6c74c14a0f510031d88d66

    conn = db.connect("agData.duckdb")
    conn.execute("""
            CREATE SCHEMA IF NOT EXISTS raw_nass
            """)

<<<<<<< HEAD
    conn.execute(f"""
                CREATE SCHEMA IF NOT EXISTS raw_nass.{sector}
                """)

=======
>>>>>>> 0c07d63c320ba1d3fa6c74c14a0f510031d88d66
    conn.execute(f"""
        CREATE OR REPLACE TABLE raw_nass.{sector}.{table_name} AS
        SELECT * FROM raw_data
        """)

<<<<<<< HEAD
    print(f"Loaded {len(raw_data)} rows into raw_nass.{sector}.{table_name}")
=======
    print(f"Loaded {len(raw_data)} rows into raw_nass.{table_name}")
>>>>>>> 0c07d63c320ba1d3fa6c74c14a0f510031d88d66

    conn.close()


if __name__ == "__main__":
<<<<<<< HEAD
    params = build_request(
                    sector="ECONOMICS", year=2002, agg_level_desc="STATE", state_name="VERMONT"
                )
    
    count = get_record_count(params)

    table_name = get_table_name(params)

    print(get_NASS_data(get_url, count, params, table_name))

    
    # northeast_states = [
    #     "CONNECTICUT",
    #     "MASSACHUSETTS",
    #     "NEW HAMPSHIRE",
    #     "VERMONT",
    #     "MAINE",
    #     "NEW YORK",
    #     "PENNSYLVANIA",
    #     "NEW JERSEY",
    #     "RHODE ISLAND",
    # ]

    # for year in [2002, 2007, 2012, 2017, 2022]:
    #     for state in northeast_states:
    #         count, params, table_name = build_request_and_get_record_count(
    #             sector="ECONOMICS", year=year, agg_level_desc="STATE", state_name=state
    #         )
    #         build_NASS_table(get_url, params, table_name, count)
    #         time.sleep(.5)
=======
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
    """
    count, params, table_name = build_request_and_get_record_count(sector="ECONOMICS", year = 2022, agg_level_desc="STATE", state_name="VERMONT")
    build_NASS_table(get_url, params, table_name, count)
    """
>>>>>>> 0c07d63c320ba1d3fa6c74c14a0f510031d88d66
