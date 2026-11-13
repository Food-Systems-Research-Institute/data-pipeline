import pandas as pd
from pathlib import Path

from utils import find_project_root

PROJECT_DIR = find_project_root()
DATA_DIR = PROJECT_DIR / "data" / "raw" / "Feeding_America_2026_MMG"


def load_xlsx_sheets(filename) -> dict[str, pd.DataFrame]:
    sheets = pd.read_excel(filename, engine="openpyxl", sheet_name=None)
    return sheets


def get__xlsx_files_from_dir_as_iter():
    files = Path(DATA_DIR).iterdir()

    return files


def load_to_duckdb(df, table_name):
    print("hello")


def run_load():
    for filename in get__xlsx_files_from_dir_as_iter():
        if filename.suffix == ".xlsx":
            print(filename)
            sheet = load_xlsx_sheets(filename)
            for sheet_name, df in sheet.items():
                table_name = "hi"
                load_to_duckdb(df, table_name)
                print(sheet_name)
                print(df)
        break

run_load()
