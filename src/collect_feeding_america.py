import pandas as pd
from pathlib import Path

from utils import find_project_root

PROJECT_DIR = find_project_root()
DATA_DIR = PROJECT_DIR / "data" / "raw" / "Feeding_America_2026_MMG"


def load_data(filename) -> pd.DataFrame:
    df = pd.read_excel(filename, engine="openpyxl")

    return df


def get_files():
    files = Path(DATA_DIR).iterdir()

    return files


def load_to_duckdb(df):
    print("hello")


def run_load():
    for filename in get_files():
        if filename.suffix == ".xlsx":
            df = load_data(filename)
            print(df.head(3))


run_load()
