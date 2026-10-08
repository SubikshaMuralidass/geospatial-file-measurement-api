import geopandas as gpd
from shapely.geometry import Polygon

from app.services.geospatial import (
    read_shapefile,
    extract_measurements,
)


def test_real_shapefile_polygon_measurement(tmp_path):
    # Create a real polygon GeoDataFrame
    polygon = Polygon([
        (80.0, 13.0),
        (80.01, 13.0),
        (80.01, 13.01),
        (80.0, 13.01),
        (80.0, 13.0),
    ])

    gdf = gpd.GeoDataFrame(
        {
            "name": ["Test Polygon"],
        },
        geometry=[polygon],
        crs="EPSG:4326",
    )

    # Write an actual Shapefile
    shapefile_path = tmp_path / "test_polygon.shp"
    gdf.to_file(shapefile_path, driver="ESRI Shapefile")

    # Read the Shapefile using our application function
    result_gdf = read_shapefile(str(shapefile_path))

    # Extract measurements using application logic
    measurements = extract_measurements(result_gdf)

    assert len(measurements) == 1

    feature = measurements[0]

    assert feature["feature_id"] == 0
    assert feature["geometry_type"] == "Polygon"
    assert feature["crs"] == "EPSG:4326"
    assert feature["status"] == "SUCCESS"

    # Area should be calculated in square meters
    assert feature["unit"] == "square_meters"
    assert feature["measurement"] is not None
    assert feature["measurement"] > 0

    # Original geometry should remain in geographic coordinates
    assert feature["geometry"]["type"] == "Polygon"
    assert feature["geometry"]["coordinates"] is not None

    # Properties should be preserved
    assert feature["properties"]["name"] == "Test Polygon"