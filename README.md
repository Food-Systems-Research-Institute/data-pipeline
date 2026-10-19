# Data Pipeline

## Development

Clone repository

```sh
git clone https://github.com/Food-Systems-Research-Institute/data-pipeline.git
cd data-pipeline
```

Set up environment with uv ([uv installation](https://github.com/Food-Systems-Research-Institute/data-pipeline.git)).

```sh
uv sync
```

### Git LFS

Using Git large file storage to hold db files. You can find [Git LFS installation here](https://git-lfs.com/), and [GitHub setup here](https://docs.github.com/en/repositories/working-with-files/managing-large-files/configuring-git-large-file-storage).

```sh
# start tracking all db files
git lfs track "*.db"
git add agData.duckdb
git commit -m "add db"
git push
```

## Running

Get a NASS API Key for free at https://quickstats.nass.usda.gov/api. Add to `.env` as `NASS_API_KEY`. Then:

```sh
uv run python src/api/collect_nass_economics.py
```

## DuckDB Schema

```sh
duckdb agData.duckdb

# See all tables
.tables

# Check schema
.schema

# Describe a specific table (schema.tablename)
DESCRIBE fips.fips_key;
```

## Contributions

Format with [Ruff](https://astral.sh/ruff), lint with [ty](https://docs.astral.sh/ty/).
