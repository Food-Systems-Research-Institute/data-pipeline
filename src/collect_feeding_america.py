# To use this script you must manually download the data folder. For instruction see collect_docs.md.
import re
from collections.abc import Iterator
from pathlib import Path

import duckdb as db
import pandas as pd

from utils import find_project_root

PROJECT_DIR = find_project_root()
DATA_DIR = PROJECT_DIR / "data" / "raw" / "Feeding_America_2026_MMG"

DB_PATH = PROJECT_DIR / "agData.duckdb"


def load_xlsx_sheets(filename) -> dict[str, pd.DataFrame]:
    sheets = pd.read_excel(filename, engine="openpyxl", sheet_name=None)
    return sheets


def get__xlsx_files_from_dir_as_iter() -> Iterator[Path]:
    files = Path(DATA_DIR).iterdir()
    print(type(files))

    return files

def create_table_name(sheet_name) -> str:
    sheet_name = "t_" + str(sheet_name)
    sheet_name = sheet_name.replace(" ", "_")
    return re.sub(r"\W+", "_", sheet_name).strip("_").lower()


def load_to_duckdb(df, table_name) -> None:
    conn = db.connect(DB_PATH)

    conn.execute("""
    CREATE SCHEMA IF NOT EXISTS feeding_america
    """)

    conn.execute(f"""
    CREATE OR REPLACE TABLE feeding_america.{table_name} AS
    SELECT * FROM df
    """)

    print(f"loaded {len(df)} rows into feeding_america.{table_name}, booyah!")

    conn.close()


def run_load() -> None:
    for filename in get__xlsx_files_from_dir_as_iter():
        if filename.suffix == ".xlsx":
            print(filename)
            sheet = load_xlsx_sheets(filename)
            for sheet_name, df in sheet.items():
                table_name = create_table_name(sheet_name)
                if not len(df):
                    continue
                load_to_duckdb(df, table_name)


if __name__ == "__main__":
    run_load()
