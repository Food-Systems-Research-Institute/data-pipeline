'''
Finds and downloads the latest release of ERS farm income data from the USDA website,
and loads into duckDB as one table
'''
import io
import re
import zipfile
from datetime import datetime
from urllib.parse import urljoin
from utils import see_tables

import duckdb as db
import pandas as pd
import requests
from bs4 import BeautifulSoup



PAGE = ("https://www.ers.usda.gov/data-products/farm-income-and-wealth-statistics/"
        "data-files-us-and-state-level-farm-income-and-wealth-statistics")

HEADERS = {"User-Agent": "vt-data-colab (contact: sshienbr@uvm.edu)"}   

con = db.connect("agData.duckDB")

RELEASE_RE = re.compile(r"([A-Z][a-z]+ \d{1,2}, \d{4}) release")

def latest_release(page_url: str):
    resp = requests.get(page_url, headers=HEADERS, timeout=60)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    h2 = soup.find("h2", string = lambda s: s and s.strip().startswith("Download All Data"))
    if h2 is None:
        raise RuntimeError("'Download All Data' heading not found; page layout changed")
    ul = h2.find_next_sibling("ul")

    releases = []
    for a in ul.find_all("a", href=True):
        m = RELEASE_RE.search(a.get_text(" ", strip=True))
        if m and a["href"].lower().endswith((".zip", ".csv")):
            date = datetime.strptime(m.group(1), "%B %d, %Y")
            releases.append((date, urljoin(page_url, a["href"])))

    if not releases:
        raise RuntimeError("Heading found but no release links parsed")
    return max(releases) # release date and url


def download_zip(url: str) -> zipfile.ZipFile:
    resp = requests.get(url, headers=HEADERS, timeout=120)
    resp.raise_for_status()
    return zipfile.ZipFile(io.BytesIO(resp.content))


def load_to_duckdb(df: pd.DataFrame, table_name: str, release_date, source_url: str):
    df = df.copy()
    df["release_date"] = release_date.date().isoformat()
    df["source_url"] = source_url

    conn = db.connect("agData.duckdb")
    conn.execute("CREATE SCHEMA IF NOT EXISTS raw_ers")
    conn.execute(f"CREATE OR REPLACE TABLE raw_ers.{table_name} AS SELECT * FROM df")
    print(f"Loaded {len(df)} rows into raw_ers.{table_name}")
    conn.close()


def clean_name(filename: str) -> str:
    stem = filename.rsplit("/", 1)[-1].rsplit(".", 1)[0]
    return "ers_farm_income_" + re.sub(r"\W+", "_", stem).strip("_").lower()


def run_collect():
    release_date, url = latest_release(PAGE)
    z = download_zip(url)

    for name in z.namelist():
        print(name)
        if not name.lower().endswith(".csv"):
            continue
        with z.open(name) as f:
            df = pd.read_csv(f, dtype=str, encoding="cp1252")
        load_to_duckdb(df, clean_name(name), release_date, url)



if __name__ == "__main__":
    run_collect()


