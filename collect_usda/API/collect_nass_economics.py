# NASS API Data Collection Script

import os
from pathlib import Path

import duckdb as db
import pandas as pd
import requests
from dotenv import load_dotenv

# Get API key from .env file
PROJECT_DIR = Path(__file__).resolve().parents[2]

load_dotenv(PROJECT_DIR / ".env")

API_KEY = os.getenv("NASS_API_KEY")


if API_KEY is None:
    print("API key not found")
else:
    print("API key loaded successfully")

param_url = "https://quickstats.nass.usda.gov/api/get_param_values/"
get_url = "https://quickstats.nass.usda.gov/api/api_GET/"
count_url = "https://quickstats.nass.usda.gov/api/get_counts/"  


# gets the categories for the descriptive parameters as a list
# (ex. param is source_desc, output is ['ANIMALS & PRODUCTS', 'CROPS', 'DEMOGRAPHICS', 'ECONOMICS', 'ENVIRONMENTAL'])
def getParams(param_url, param):
    param_params = {"key": API_KEY, "param": param}

    param_response = requests.get(param_url, params=param_params, timeout=60)

    print("Status code:", param_response.status_code)
    print("Response preview:", param_response.text[:1000])
    return param_response.json()[param]

def build_request_and_get_record_count(sector, group, year, agg_level_desc=None, state_name=None, county_name=None, zip_5=None):
    params = {
                "key": API_KEY,
                "format": "JSON",
                "source_desc": "CENSUS",
                "sector_desc": sector,
                "group_desc": group,
                "year": year,
            }
    if agg_level_desc is not None:
        params["agg_level_desc"] = agg_level_desc

    if state_name is not None:
        params["state_name"] = state_name

    if county_name is not None:
        params["county_name"] = county_name

    if zip_5 is not None:
        params["zip_5"] = zip_5
    
    response = requests.get(count_url,
                            params = params,
                            timeout=60)


    table_parts = [sector, group]

    if agg_level_desc:
        table_parts.append(agg_level_desc)
    if state_name:
        table_parts.append(state_name)
    if county_name:
        table_parts.append(county_name)
    if zip_5:
        table_parts.append(zip_5)

    table_parts.append(str(year))
    table_name = "_".join(table_parts).replace(" ", "_").lower()

    return int(response.json()["count"]), params, table_name



# Get raw data from NASS API based on the specified parameters
def get_NASS_data(get_url, row_count, params):
    if row_count > 50.000:
        print(f"Request to large({row_count} rows), try further filtering")
        return None
    response = requests.get(get_url, params=params, timeout=60)
    print("Status code:", response.status_code)
    print("Response preview:", response.text[:1000])


    if response.status_code != 200:
        print(f"Request failed for {table_name}: {response.text[:500]}")
        return pd.DataFrame()

    raw_data = response.json()

    if "data" not in raw_data:
        print(f"No data field for {table_name}: {raw_data}")
        return pd.DataFrame()

    return pd.DataFrame(raw_data["data"])


def build_NASS_table(get_url, params, table_name, row_count):
    raw_data = get_NASS_data(get_url, row_count, params)
    
    if raw_data is None:
            print("build table failed, request was too large")
            return None
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
    count, params, table_name = build_request_and_get_record_count(sector="ECONOMICS", group="EXPENSES", year = 2022)
    print(count, params, table_name)
    build_NASS_table(get_url, params, table_name, count)