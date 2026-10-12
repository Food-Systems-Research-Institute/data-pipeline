import duckdb as db
import re
from io import StringIO

import tkinter as tk
from tkinter import filedialog


def get_file_path_and_table_name():
    root = tk.Tk()
    root.withdraw()

    FILE_PATH = filedialog.askopenfilename()

    # Replace with desired name of table
    TABLE_NAME = FILE_PATH.split("/")[-1].replace("qs.", "").replace(".txt", "")
    return FILE_PATH, TABLE_NAME


def load_to_db(filepath, table_name):
    conn = db.connect("agData.duckdb")
    cursor = conn.cursor()
    cursor.execute(f"""
    CREATE TABLE IF NOT EXISTS {table_name} AS 
    SELECT * REPLACE (
        TRY_CAST(REPLACE(VALUE, ',', '') AS BIGINT) AS VALUE
    )
    FROM read_csv('{filepath}', all_varchar = true)
    """)
    conn.commit()
    cursor.close()
    conn.close()
    print(f"Loaded {filepath} into {table_name}")
   

if __name__ == "__main__":
    FILE_PATH, TABLE_NAME = get_file_path_and_table_name()
    load_to_db(FILE_PATH, TABLE_NAME)


    
    
