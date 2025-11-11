import tlproject

import numpy as np

import geopandas as gpd
import rasterio
from rasterio.warp import reproject, Resampling, calculate_default_transform
from pyproj import Transformer

class DEM:
    def __init__(self, infos_unique):
        if tlproject.dem_file is not None:
            src = rasterio.open(tlproject.dem_file)
            dst_crs = "EPSG:32632"
            # Berechne Transformation und neue Dimensionen
            transform, width, height = calculate_default_transform(
                src.crs, dst_crs, src.width, src.height, *src.bounds)
            # Initialisiere ein Array für die transformierten Daten
            self.matrix = np.empty((height, width), dtype=src.meta['dtype'])
            # Transformiere das Raster
            reproject(
                source=src.read(1),
                destination=self.matrix,
                src_transform=src.transform,
                src_crs=src.crs,
                dst_transform=transform,
                dst_crs=dst_crs,
                resampling=Resampling.nearest
            )

            self.extent = [transform[2], transform[2] + width * transform[0],
                          transform[5] + height * transform[4], transform[5]]
        else:
            self.extent = [0, 1, 0, 1]