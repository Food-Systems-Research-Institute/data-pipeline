import zipfile

import geopandas as gpd

from spatial_utils import get_zonal_stats, mask_rasters
from utils import find_project_root

# Download for example
# https://www.mrlc.gov/data

county_shapefiles = (
    "https://www2.census.gov/geo/tiger/GENZ2024/shp/cb_2024_us_county_20m.zip"
)

PROJECT_DIR = find_project_root()
NLCD_ZIP = PROJECT_DIR / "smdata_migration" / "Annual_NLCD_LndCov_2025_CU_C1V2.zip"
WORK_DIR = PROJECT_DIR / "smdata_migration" / "nlcd"
CONUS_DIR = WORK_DIR / "conus"
NEAST_DIR = WORK_DIR / "neast"
AOI_PATH = WORK_DIR / "neast_mask.gdb"
COUNTY_PATH = WORK_DIR / "neast_counties.gdb"
neast_states = ["CT", "ME", "MA", "NH", "NJ", "NY", "PA", "RI", "VT"]

counties = gpd.read_file(county_shapefiles)
print(counties)
counties = counties[counties["STUSPS"].isin(neast_states)]
print(counties)
counties = counties.rename(columns={"GEOID": "fips"})
print(counties)

# Reproject to equal area
counties.crs
counties = counties.to_crs(5070)
counties["area_km2"] = counties.area / 1e6
counties.info()

# Dissolve to states
states = counties.dissolve(
    by="STUSPS", aggfunc={"fips": "count", "area_km2": "sum"}
).rename(columns={"fips": "n_counties"})

# Save states to gdb
states.to_file(
    PROJECT_DIR / "smdata_migration" / "states.gdb",
    driver="OpenFileGDB",
    promote_to_multi=True,
    layer="states",
)

# Dissolve into single shape for mask
neast_mask = gpd.GeoDataFrame(geometry=[counties.union_all()], crs=counties.crs)
print(neast_mask)
neast_mask.info()
type(neast_mask)

for d in (CONUS_DIR, NEAST_DIR):
    d.mkdir(parents=True, exist_ok=True)

with zipfile.ZipFile(NLCD_ZIP) as zf:
    tif_name = next(n for n in zf.namelist() if n.endswith(".tif"))
    if not (CONUS_DIR / tif_name).exists():
        zf.extract(tif_name, CONUS_DIR)

neast_mask.to_file(
    AOI_PATH, driver="OpenFileGDB", promote_to_multi=True, layer="neast_mask"
)
counties[["fips", "geometry"]].to_file(
    COUNTY_PATH, driver="OpenFileGDB", promote_to_multi=True, layer="neast_counties"
)

masked_tif = NEAST_DIR / tif_name.replace(".tif", "_masked.tif")
if not masked_tif.exists():
    mask_rasters(str(CONUS_DIR), str(NEAST_DIR), str(AOI_PATH))

# Most common land cover class code in each county
lulc_class = get_zonal_stats(
    str(masked_tif),
    str(COUNTY_PATH),
    "majority",
    "lc_majority",
)
counties = counties.merge(lulc_class, on="fips")
counties["lc_majority"] = counties["lc_majority"].astype(int).astype(str)
print(counties["lc_majority"].value_counts())
