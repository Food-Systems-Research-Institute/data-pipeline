# NASS API Data Collection Script

import os

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


# gets the categories for the descriptive parameters as a list
# (ex. param is source_desc, output is ['ANIMALS & PRODUCTS', 'CROPS', 'DEMOGRAPHICS', 'ECONOMICS', 'ENVIRONMENTAL'])
def getParams(param_url, param):
    param_params = {"key": API_KEY, "param": param}

    param_response = requests.get(param_url, params=param_params, timeout=60)

    print("Status code:", param_response.status_code)
    print("Response preview:", param_response.text[:1000])
    return param_response.json()[param]


# Get economics data from NASS API for each group within the ECONOMICS sector
def get_economics_data(get_url, group):
    params = {
        "key": API_KEY,
        "format": "JSON",
        "source_desc": "CENSUS",
        "sector_desc": "ECONOMICS",
        "group_desc": group,
        "agg_level_desc": "STATE",
        "state_alpha": "VT",
    }

    response = requests.get(get_url, params=params, timeout=60)
    print("Status code:", response.status_code)
    print("Response preview:", response.text[:1000])

    if response.status_code != 200:
        print(f"Request failed for {group}: {response.text[:500]}")
        return pd.DataFrame()

    econ_data = response.json()

    if "data" not in econ_data:
        print(f"No data field for {group}: {econ_data}")
        return pd.DataFrame()

    return pd.DataFrame(econ_data["data"])


def build_economics_table():
    econ_groups = [
        "ENERGY",
        "EXPENSES",
        "FARMS & LAND & ASSETS",
        "INCOME",
        "IRRIGATION",
        "PRICES PAID",
    ]

    conn = db.connect("agData.duckdb")
    conn.execute("""
            CREATE SCHEMA IF NOT EXISTS economics
            """)

    for group in econ_groups:
        econ_data = get_economics_data(get_url, group)

        if econ_data.empty:
            print(f"No data returned for {group}")
            continue

        table_name = group.lower().replace(" & ", "_").replace(" ", "_")

        conn.register("econ_data", econ_data)

        conn.execute(f"""
        CREATE OR REPLACE TABLE economics.{table_name} AS
        SELECT * FROM econ_data
        """)

        conn.unregister("econ_data")

        print(f"Loaded {len(econ_data)} rows into economics.{table_name}")

    conn.close()


if __name__ == "__main__":
    build_economics_table()
