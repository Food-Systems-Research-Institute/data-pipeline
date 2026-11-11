import glob
import os

import geopandas as gpd
import pandas as pd
import rasterio
import rasterstats
from rasterio.mask import mask


def get_zonal_stats(
    raster_path: str,
    polygon_path: str,
    stat: str,
    new_name: str,
    missing: str | None = None,
) -> pd.DataFrame:
    """
    Run zonal_stats given a path to a raster and path to a polygon.

    Args:
      raster_path (str): File path to a raster file (.tif)
      polygon_path (str): File path to a polygon (.gpkg, .shp)
      stat (str): Type of statistic to run (min, max, sum, median, mean)
      missing (str): Code for missing values to be removed.

    Returns:
      DataFrame
    """

    # Get raster crs
    with rasterio.open(raster_path) as src:
        raster_crs = src.crs

    # Load polygons shapefile
    polygons = gpd.read_file(polygon_path)

    # If CRS do not match, convert polygons to CRS of raster
    if polygons.crs != raster_crs:
        polygons = polygons.to_crs(raster_crs)

    # Calculate stat of raster value within each polygon
    out = rasterstats.zonal_stats(
        polygons, raster_path, stats=stat, geojson_out=True, nodata=missing
    )

    # Return a data frame
    df = gpd.GeoDataFrame.from_features(out)
    df.set_crs(polygons.crs, inplace=True)
    df = pd.DataFrame(df)
    df = df[["fips", stat]]
    df.rename(columns={stat: new_name}, inplace=True)
    return df


def mask_rasters(input_dir: str, output_dir: str, aoi_path: str) -> None:
    """
    Reduces folder of rasters to Northeast states using mask file and saves to
    a new folder.

    Args:
      input_dir (str): File path to where large conus rasters are kept
      output_dir (str): File path to where smaller Northeast rasters should go
      aoi_path (str): File path to a mask object of the Northeast

    Returns:
      Nothing. Just saves the rasters of the Northeast in the output folder.
    """

    # Load area of interest
    aoi = gpd.read_file(aoi_path)
    aoi = aoi.to_crs("EPSG:4326")  # project to wgs 84 just in case

    # Convert geometries to GeoJSON-like dicts for rasterio.mask
    geoms = aoi.geometry.values
    geoms = [geom.__geo_interface__ for geom in geoms]

    # Get a list of all the tif files, print to check
    tif_files = glob.glob(os.path.join(input_dir, "*.tif"))
    print(tif_files)

    # Loop through all tif files, mask, save
    for tif in tif_files:
        with rasterio.open(tif) as src:
            # Reproject shapes just in case
            if src.crs != aoi.crs:
                aoi_proj = aoi.to_crs(src.crs)
                geoms_proj = [geom.__geo_interface__ for geom in aoi_proj.geometry]
            else:
                geoms_proj = geoms

            # Mask raster with AOI
            out_image, out_transform = mask(src, geoms_proj, crop=True)
            out_meta = src.meta.copy()

            # Update metadata
            out_meta.update(
                {
                    "driver": "GTiff",
                    "height": out_image.shape[1],
                    "width": out_image.shape[2],
                    "transform": out_transform,
                }
            )

            # Output file path
            out_name = os.path.basename(tif).replace(".tif", "_masked.tif")
            out_path = os.path.join(output_dir, out_name)

            # Save the masked raster
            with rasterio.open(out_path, "w", **out_meta) as dest:
                dest.write(out_image)

    print("Masking complete. Northeast rasters saved in:", output_dir)


def raster_mean_by_polygon(polygon_path, raster_path, new_name) -> pd.DataFrame:

    # Get raster crs
    with rasterio.open(raster_path) as src:
        raster_crs = src.crs

    # Load polygons shapefile
    polygons = gpd.read_file(polygon_path)

    # If CRS do not match, convert polygons to CRS of raster
    if polygons.crs != raster_crs:
        polygons = polygons.to_crs(raster_crs)

    # Calculate mean of raster value within each polygon
    out = rasterstats.zonal_stats(polygons, raster_path, stats="mean", geojson_out=True)

    # Return a data frame
    df = gpd.GeoDataFrame.from_features(out)
    df.set_crs(polygons.crs, inplace=True)
    df = pd.DataFrame(df)
    df = df[["fips", "mean"]]
    df.rename(columns={"mean": new_name}, inplace=True)
    return df


def cat_zonal_stats(
    raster_path: str, polygon_path: str, missing: str | None = None
) -> pd.DataFrame:
    """
    Get a DataFrame of LULC category cell counts for each polygon. If the CRS of
    each file do not match, the polygons will be projected into the CRS of the
    raster.

    Args:
      raster_path (str): File path to a raster file (.tif)
      polygon_path (str): File path to a polygon (.gpkg, .shp)

    Returns:
      DataFrame
    """

    # Load polygon file
    polygons = gpd.read_file(polygon_path)

    # Save CRS from raster as object without loading raster
    with rasterio.open(raster_path) as src:
        raster_crs = src.crs

    # If CRS is different, transform polygons to same crs as raster
    if polygons.crs != raster_crs:
        print(f"Transforming polygon CRS from {polygons.crs} to {raster_crs}")
        polygons = polygons.to_crs(raster_crs)

    # Calculate frequency of each LULC class within each polygon
    # Note that we use polygon file, but only raster path
    out = rasterstats.zonal_stats(
        polygons, raster_path, stats=None, categorical=True, nodata=missing
    )

    # Convert to dataframe, put fips column back in
    df = pd.DataFrame(out)
    df["fips"] = polygons["fips"]
    return df
