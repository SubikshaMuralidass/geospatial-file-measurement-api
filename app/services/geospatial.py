import geopandas as gpd
import math
import numpy as np
from shapely.geometry import mapping


def read_kml(file_path: str) -> gpd.GeoDataFrame:
    return gpd.read_file(
        file_path,
        driver="KML",
    )


def read_shapefile(file_path: str) -> gpd.GeoDataFrame:
    return gpd.read_file(file_path)


def clean_value(value):
    """Convert values into JSON-safe Python values."""
    if value is None:
        return None

    if isinstance(value, np.generic):
        value = value.item()

    if isinstance(value, float):
        if not math.isfinite(value):
            return None

    return value


def clean_geometry(geometry):
    """Convert Shapely geometry mapping into JSON-safe values."""
    data = mapping(geometry)

    def clean_nested(value):
        if isinstance(value, (list, tuple)):
            return [clean_nested(item) for item in value]

        if isinstance(value, np.generic):
            value = value.item()

        if isinstance(value, float):
            return value if math.isfinite(value) else None

        return value

    return clean_nested(data)


def extract_measurements(gdf: gpd.GeoDataFrame) -> list[dict]:
    if gdf.crs is None:
        raise ValueError(
            "The geospatial file does not contain CRS information."
        )

    original_crs = gdf.crs.to_string()

    # Find a suitable projected CRS for metric calculations.
    projected_crs = gdf.estimate_utm_crs()

    if projected_crs is None:
        raise ValueError(
            "Unable to determine a suitable projected CRS."
        )

    # Keep original geometry/coordinates for the API response.
    original_gdf = gdf

    # Use projected geometry only for area and length calculations.
    projected_gdf = gdf.to_crs(projected_crs)

    measurements = []

    for index in original_gdf.index:
        original_row = original_gdf.loc[index]
        projected_row = projected_gdf.loc[index]

        original_geometry = original_row.geometry
        projected_geometry = projected_row.geometry

        geometry_type = original_geometry.geom_type

        # Convert NumPy index values to normal Python values.
        feature_id = (
            index.item()
            if isinstance(index, np.generic)
            else index
        )

        feature = {
            "feature_id": feature_id,
            "geometry_type": geometry_type,
            "geometry": clean_geometry(original_geometry),
            "crs": original_crs,
            "properties": {
                key: clean_value(value)
                for key, value in original_row.items()
                if key != "geometry"
            },
            "measurement": None,
            "unit": None,
            "status": "SUCCESS",
        }

        # Polygon → area
        if geometry_type in ("Polygon", "MultiPolygon"):
            measurement = float(projected_geometry.area)

            if math.isfinite(measurement):
                feature["measurement"] = measurement
                feature["unit"] = "square_meters"
            else:
                feature["status"] = "INVALID_MEASUREMENT"

        # LineString → length
        elif geometry_type in ("LineString", "MultiLineString"):
            measurement = float(projected_geometry.length)

            if math.isfinite(measurement):
                feature["measurement"] = measurement
                feature["unit"] = "meters"
            else:
                feature["status"] = "INVALID_MEASUREMENT"

        # Point → no measurement
        elif geometry_type in ("Point", "MultiPoint"):
            feature["status"] = "NO_MEASUREMENT"

        # Any unsupported geometry → continue processing
        else:
            feature["status"] = "UNSUPPORTED"

        measurements.append(feature)

    return measurements