from pathlib import Path

import duckdb

conn = duckdb.connect(str(Path(__name__).parent.parent / "agData.duckdb"), read_only=True)

energy = conn.execute("SELECT * FROM economics.energy").df()
expenses = conn.execute("SELECT * FROM economics.expenses").df()

print(energy.head())
print(energy.shape)
print(energy.dtypes)
print(energy.location_desc.unique())
print(energy.describe())
print(energy.isnull().sum())

conn.close()
