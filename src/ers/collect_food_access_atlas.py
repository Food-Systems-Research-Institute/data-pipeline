# import requests
# PAGE = "https://www.ers.usda.gov/data-products/food-access-research-atlas/download-the-data"
# HEADERS = {"User-Agent": "vt-data-colab (contact: you@example.org)"}
# html = requests.get(PAGE, headers=HEADERS, timeout=60).text
# print(len(html))
# i = html.find("<main")
# print(html[i:i+9000])
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

def find_downloads(page_url: str = PAGE):
    resp = requests.get(page_url, headers=HEADERS, timeout=60)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    drawer = soup.find(id="drawer-0")          # the "Current Versions" section
    if drawer is None:
        raise RuntimeError("'Current Versions' section not found; page layout changed")

    found = []
    for item in drawer.select("li.usa-collection__item"):
        heading = item.select_one(".usa-collection__heading")
        if heading is None:
            continue
        title = heading.get_text(" ", strip=True)
        for a in item.find_all("a", href=True):
            path = a["href"].split("?")[0].lower()      # drop ?v=12345
            if path.endswith(".zip"):
                found.append((title, urljoin(page_url, a["href"])))
    return found

def download_zip(url: str) -> zipfile.ZipFile:
    resp = requests.get(url, headers=HEADERS, timeout=300)
    resp.raise_for_status()
    return zipfile.ZipFile(io.BytesIO(resp.content))

if __name__ == "__main__":
    for title, url in find_downloads():
        z = download_zip(url)
        print(title)
        for info in z.infolist():
            print("   ", info.filename, info.file_size)
