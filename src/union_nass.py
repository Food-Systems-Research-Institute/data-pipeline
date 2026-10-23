import duckdb as db


def union_nass_tables():
    conn = db.connect("agData.duckdb")