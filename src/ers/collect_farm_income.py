from bs4 import BeautifulSoup
import duckdb as db
import requests

con = db.connect("agData.duckDB")

ERS_PAGE_URL = "https://www.ers.usda.gov/data-products?type=downloadable-data-files"

def find_csv_links(page_url: str):
    response = requests.get(ERS_PAGE_URL, timeout=30)
    response.raise_for_status()

    parser = BeautifulSoup(response.text, 'html.parser')

    print(parser.prettify)

find_csv_links(ERS_PAGE_URL)

