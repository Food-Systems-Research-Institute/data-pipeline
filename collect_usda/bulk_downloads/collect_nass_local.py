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
        

'''
def get_columns(FILE_PATH_FINAL):
    column_names = ""
    with open(FILE_PATH_FINAL, "r") as file:
        columns = file.readline().strip().split("\t")

    for column in columns:
        column = re.sub(r"[^a-zA-Z0-9_]", "_", column).lower()
        column_names += f"    {column} TEXT,\n"

    return column_names.rstrip(",\n")


def create_table():
    conn = db.connect("agData.db")
    cursor = conn.cursor()

    columns = get_columns(FILE_PATH_FINAL)

    cursor.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
        {columns}
        );
        """
    )
    conn.commit()
    cursor.close()
    conn.close()


def load_data():
    conn = db.connect("agData.db")
    cursor = conn.cursor()

    with open(FILE_PATH_FINAL, "r", encoding="utf-8", errors="replace") as f:
        cursor.copy_expert(
        f"""
            COPY {TABLE_NAME}
            FROM STDIN
            WITH (
                FORMAT csv,
                HEADER true,
                DELIMITER E'\\t',
                NULL ''
            );
            """,
        f,
    )

    conn.commit()
    cursor.close()
    conn.close()

    print(f"Loaded {FILE_PATH_FINAL} into {TABLE_NAME}")
'''

if __name__ == "__main__":
    FILE_PATH, TABLE_NAME = get_file_path_and_table_name()
    load_to_db(FILE_PATH, TABLE_NAME)


    
    
