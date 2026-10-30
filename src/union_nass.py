import duckdb as db


def union_nass_tables(sector: str, agg_level: str):
    conn = db.connect("agData.duckdb")

    concat_table = sector + "_" + agg_level

    conn.execute("""
                SELECT * FROM 
        
    
    """)
