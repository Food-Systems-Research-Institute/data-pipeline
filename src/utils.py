from functools import cache
from pathlib import Path

import pandas as pd


def find_project_root(
    config_name: str = "pyproject.toml", start: Path | None = None
) -> Path:
    """Walk up directories until you find config file.

    Args:
        config_name: Name of config file to find. Defaults to "pyproject.toml"
        start: Path to start walking from. Defaults to None.

    Returns:
        Path: Absolute path to project root
    """
    current_path = (start or Path.cwd()).resolve()
    while current_path != current_path.parent:
        if (current_path / config_name).exists():
            return current_path
        current_path = current_path.parent

    if (current_path / config_name).exists():
        return current_path

    return (start or Path.cwd()).resolve()


def load_fips_key(db_path: str = "agData.duckdb"):
    """Load FIPS key with county and state fips, names, for Northeast states"""
    import duckdb

    conn = duckdb.connect(db_path)
    conn.execute("CREATE SCHEMA IF NOT EXISTS fips")

    csv_path = Path(__file__).parent / "reference" / "fips_key.csv"
    conn.execute(
        "CREATE OR REPLACE TABLE fips.fips_key AS SELECT * FROM read_csv_auto($path, header = true, nullstr = 'NA', types = {'fips': 'VARCHAR'})",
        {"path": str(csv_path)},
    )

    conn.close()


@cache
def fips_key() -> pd.DataFrame:
    """FIPS lookup table for Northeast states, cached as data frame"""
    import pandas as pd

    csv_path = Path(__file__).parent / "reference" / "fips_key.csv"
    df = pd.read_csv(csv_path, dtype={"fips": str})
    df.columns = ["idx", "fips", "county_name", "state_name", "state_code"]

    # Add state codes to all counties as well as states (counties had NA state code)
    state_map = df.dropna(subset=["state_code"]).set_index("state_name")["state_code"]
    df["state_code"] = df["state_code"].fillna(df["state_name"].map(state_map))

    return df
