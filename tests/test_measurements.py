import geopandas as gpd
from shapely.geometry import LineString, Point, Polygon

from app.services.geospatial import extract_measurements


def test_point_has_no_measurement():
    gdf = gpd.GeoDataFrame(
        {"name": ["Test Point"]},
        geometry=[Point(77.5946, 12.9716)],
        crs="EPSG:4326",
    )

    result = extract_measurements(gdf)

    assert result[0]["geometry_type"] == "Point"
    assert result[0]["measurement"] is None
    assert result[0]["unit"] is None
    assert result[0]["status"] == "NO_MEASUREMENT"


def test_linestring_returns_length():
    line = LineString([
        (77.5946, 12.9716),
        (77.6046, 12.9716),
    ])

    gdf = gpd.GeoDataFrame(
        {"name": ["Test Line"]},
        geometry=[line],
        crs="EPSG:4326",
    )

    result = extract_measurements(gdf)

    assert result[0]["geometry_type"] == "LineString"
    assert result[0]["measurement"] is not None
    assert result[0]["measurement"] > 0
    assert result[0]["unit"] == "meters"
    assert result[0]["status"] == "SUCCESS"


def test_polygon_returns_area():
    polygon = Polygon([
        (77.5946, 12.9716),
        (77.6046, 12.9716),
        (77.6046, 12.9816),
        (77.5946, 12.9816),
        (77.5946, 12.9716),
    ])

    gdf = gpd.GeoDataFrame(
        {"name": ["Test Polygon"]},
        geometry=[polygon],
        crs="EPSG:4326",
    )

    result = extract_measurements(gdf)

    assert result[0]["geometry_type"] == "Polygon"
    assert result[0]["measurement"] is not None
    assert result[0]["measurement"] > 0
    assert result[0]["unit"] == "square_meters"
    assert result[0]["status"] == "SUCCESS"


def test_original_crs_is_preserved():
    point = Point(77.5946, 12.9716)

    gdf = gpd.GeoDataFrame(
        {"name": ["Test"]},
        geometry=[point],
        crs="EPSG:4326",
    )

    result = extract_measurements(gdf)

    assert result[0]["crs"] == "EPSG:4326"


def test_multiple_features():
    gdf = gpd.GeoDataFrame(
        {"name": ["point", "line"]},
        geometry=[
            Point(77.5946, 12.9716),
            LineString([
                (77.5946, 12.9716),
                (77.6046, 12.9716),
            ]),
        ],
        crs="EPSG:4326",
    )

    result = extract_measurements(gdf)

    assert len(result) == 2

    assert result[0]["geometry_type"] == "Point"
    assert result[0]["status"] == "NO_MEASUREMENT"

    assert result[1]["geometry_type"] == "LineString"
    assert result[1]["status"] == "SUCCESS"