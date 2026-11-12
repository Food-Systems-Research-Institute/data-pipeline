import importlib
from pathlib import Path

import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import pygris
import rasterio
import rasterio.windows
from rasterio.plot import show

import spatial_utils

importlib.reload(spatial_utils)
from spatial_utils import cat_zonal_stats, mask_raster
from utils import find_project_root

ROOT = find_project_root()
DIR = ROOT / "smdata_migration/spatial"


# Raster --------------------------------------------------------------------

cdl_path = Path(DIR / "2025_cultivated_layer/2025_cultivated_layer.tif")
cdl = rasterio.open(cdl_path)

# Slice
print(cdl.shape)
np.set_printoptions(linewidth=100)

small = cdl.read(1, out_shape=(cdl.height // 100, cdl.width // 100))
print(small.shape)
print(small[500:510, 600:610])
show(small)
plt.show()

dir(cdl)

# CRS coordinate reference system
crs = cdl.crs
print(crs)  # geodetic parameter dataset (euro petroleum survey group?)
crs
dir(crs)
print(crs.is_projected)
print(crs.linear_units)

# other things
dir(cdl)
print(cdl.profile)  # all metadata
print(cdl.bounds)
print(cdl.statistics)
cdl.tags()
cdl.tags(1)

cdl.close()


# Vector ------------------------------------------------------------------

vt = pygris.counties(state="Vermont")
print(vt)

# Explore
dir(vt)
print(vt.shape)
print(vt.crs)

# Plot
vt.plot()
plt.show()

vt.plot(column="ALAND")
plt.show()

vt.explore().save("smdata_migration/vt_counties.html")


# Mask and Clip -----------------------------------------------------------

# First deal with projections
print(vt.crs)
vt = vt.to_crs(5070)
print(vt.crs)
assert vt.crs == cdl.crs == 5070

# Dissolve for mask
vt_mask = vt.dissolve()
vt_mask.plot()
plt.show()

# Save files for masking function
vt_counties_path = DIR / "vt_counties.gpkg"
vt.to_file(vt_counties_path)
mask_path = DIR / "vt_mask.gpkg"
vt_mask.to_file(mask_path)

cdl_ne_path = DIR / "cdl_ne.tif"
mask_raster(str(cdl_path), str(cdl_ne_path), str(mask_path))

cdl_ne = rasterio.open(cdl_ne_path)
print(cdl_ne.bounds)
show(cdl_ne)
plt.show()

cdl_ne.close()


# Zonal Stats -----------------------------------------------------------

out = cat_zonal_stats(str(cdl_ne_path), str(vt_counties_path), identifier="COUNTYFP")
print(out)
