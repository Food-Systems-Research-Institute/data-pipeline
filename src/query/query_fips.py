
from pathlib import Path
import re
from utils import find_project_root

import duckdb

PROJECT_DIR = find_project_root()
DB_PATH = PROJECT_DIR / "agData.duckdb"


def query_county(fips_code:str, schema: str, table: str):
        """Retrieve records for a county using its FIPS codes table."""

        # validate schema and table names before SQL query
        for identifier in (schema, table):
            if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", identifier):
                raise ValueError(f"Invalid SQL identifier: {identifier}")

        state_fips = fips_code[:2]
        county_fips = fips_code[2:]

        conn = duckdb.connect(str(DB_PATH), read_only=True)
        result = conn.execute(f"""
        SELECT * FROM {schema}.{table}
        WHERE state_fips = ? AND
        WHERE county_fips = ?;
        """,
        [state_fips, county_fips],
        ).fetchdf()

        return result


if __name__ == "__main__":
    result = query_county("50007", "raw_nass", "economics_county_vermont_2022")
    print(result.head(10))




    
