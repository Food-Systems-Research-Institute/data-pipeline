import io
import re
import zipfile
from urllib.parse import urljoin

import duckdb as db
import pandas as pd
import requests
from bs4 import BeautifulSoup

PAGE = "https://www.ers.usda.gov/data-products/food-access-research-atlas/download-the-data"
HEADERS = {"User-Agent": "vt-data-colab (contact: you@example.org)"}
DB_PATH = "agData.duckdb"


def find_downloads(page_url: str = PAGE) -> list[tuple[str, str]]:
    """Return [(title, zip_url), ...] from the 'Current Versions' section."""
    resp = requests.get(page_url, headers=HEADERS, timeout=60)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    drawer = soup.find(id="drawer-0")
    if drawer is None:
        raise RuntimeError("'Current Versions' section not found; page layout changed")

    found = []
    for item in drawer.select("li.usa-collection__item"):
        heading = item.select_one(".usa-collection__heading")
        if heading is None:
            continue
        title = heading.get_text(" ", strip=True)
        for a in item.find_all("a", href=True):
            if a["href"].split("?")[0].lower().endswith(".zip"):
                found.append((title, urljoin(page_url, a["href"])))
    return found


def download_zip(url: str) -> zipfile.ZipFile:
    resp = requests.get(url, headers=HEADERS, timeout=300)
    resp.raise_for_status()
    return zipfile.ZipFile(io.BytesIO(resp.content))


def dataset_year(title: str) -> str:
    """'2025 SNAP-authorized ...' -> '2025'"""
    m = re.match(r"\s*(\d{4})", title)
    if not m:
        raise ValueError(f"No year at start of title: {title}")
    return m.group(1)


def clean_name(year: str, filename: str) -> str:
    stem = filename.rsplit("/", 1)[-1].rsplit(".", 1)[0]
    slug = re.sub(r"\W+", "_", stem).strip("_").lower()
    return f"ers_food_access_{year}_{slug}"


def read_csv_bytes(data: bytes) -> pd.DataFrame:
    for enc in ("utf-8-sig", "cp1252"):
        try:
            return pd.read_csv(io.BytesIO(data), dtype=str, encoding=enc)
        except UnicodeDecodeError:
            continue
    raise ValueError("Could not decode CSV")


def load_to_duckdb(
    df: pd.DataFrame, table_name: str, dataset: str, source_url: str
) -> None:
    df = df.copy()
    df["dataset"] = dataset
    df["source_url"] = source_url

    conn = db.connect(DB_PATH)
    conn.execute("CREATE SCHEMA IF NOT EXISTS raw_ers")
    conn.execute(f'CREATE OR REPLACE TABLE raw_ers."{table_name}" AS SELECT * FROM df')
    print(f"Loaded {len(df):,} rows into raw_ers.{table_name}")
    conn.close()


def load_dataset(title: str, url: str) -> None:
    year = dataset_year(title)
    z = download_zip(url)
    for name in z.namelist():
        if not name.lower().endswith(".csv"):
            continue
        df = read_csv_bytes(z.read(name))
        load_to_duckdb(df, clean_name(year, name), title, url)


def run_collect() -> None:
    for title, url in find_downloads():
        print(f"\n{title}")
        load_dataset(title, url)


if __name__ == "__main__":
    run_collect()
