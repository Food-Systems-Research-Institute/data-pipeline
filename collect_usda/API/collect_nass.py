# NASS API Data Collection Script

import os
import requests 
from dotenv import load_dotenv
from pathlib import Path 


#Get API key from .env file
PROJECT_DIR = Path(__file__).resolve().parent

load_dotenv(PROJECT_DIR / ".env")

API_KEY = os.getenv("NASS_API_KEY")


if API_KEY is None:
    print("API key not found")
else:
    print("API key loaded successfully")

param_url = "https://quickstats.nass.usda.gov/api/get_param_values/"



def getParams(param_url, param):
    param_params = {
        "key": API_KEY,
        "param": param
    }

    param_response = requests.get(
        param_url,
        params=param_params,
        timeout=60
    )

    print("Status code:", param_response.status_code)
    print("Response preview:", param_response.text[:1000])
    return param_response.json()[param]

params = ["source_desc", "sector_desc", "group_desc", "commodity_desc"]
sector_params =getParams(param_url, "sector_desc")
print(sector_params)


#def build_table

'''
param_response = requests.get(
    param_url,
    params=param_params,
    timeout=60
)

print("Status code:", param_response.status_code)
print("Response preview:", param_response.text[:1000])



url = "https://quickstats.nass.usda.gov/api/api_GET/"

params = {
    "key": API_KEY,
    "format": "JSON",
    "commodity_desc": "CORN",
    "statisticcat_desc": "PRODUCTION",
    "agg_level_desc": "STATE",
    "state_alpha": "VT",
    "year": "2022"
}


params = {
    "key": API_KEY,
    "param": "commodity_desc"
}


response = requests.get(url, params=params, timeout=60)

print("Status code:", response.status_code)
print("Response URL:", response.url)
print("Response preview:", response.text[:500])

result = response.json()

print(type(result))
print(result.keys())
print(len(result["data"]))

print("Result data 1: ", result['data'][0].keys())

'''
