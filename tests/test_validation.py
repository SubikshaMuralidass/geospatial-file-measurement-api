from io import BytesIO
from zipfile import ZipFile

from app.services.file_validator import (
    MAX_SHAPEFILE_ZIP_SIZE,
    validate_file,
    validate_kml,
    validate_shapefile_zip,
)


def test_kml_file_is_accepted():
    result = validate_file("test.kml")

    assert result["valid"] is True
    assert result["file_type"] == "kml"


def test_shapefile_zip_is_accepted():
    result = validate_file(
        "test.zip",
        file_size=1000,
    )

    assert result["valid"] is True
    assert result["file_type"] == "shapefile"


def test_shapefile_zip_exactly_2gb_is_accepted():
    result = validate_file(
        "test.zip",
        file_size=MAX_SHAPEFILE_ZIP_SIZE,
    )

    assert result["valid"] is True


def test_shapefile_zip_over_2gb_is_rejected():
    result = validate_file(
        "test.zip",
        file_size=MAX_SHAPEFILE_ZIP_SIZE + 1,
    )

    assert result["valid"] is False
    assert "2 GB" in result["message"]


def test_unsupported_extension_is_rejected():
    result = validate_file("test.pdf")

    assert result["valid"] is False
    assert result["file_type"] is None


def create_test_shapefile_zip():
    file_object = BytesIO()

    with ZipFile(file_object, "w") as zip_file:
        zip_file.writestr("roads.shp", b"dummy")
        zip_file.writestr("roads.shx", b"dummy")
        zip_file.writestr("roads.dbf", b"dummy")

    file_object.seek(0)
    return file_object


def test_valid_shapefile_zip():
    file_object = create_test_shapefile_zip()

    result = validate_shapefile_zip(file_object)

    assert result["valid"] is True


def test_shapefile_zip_missing_required_file():
    file_object = BytesIO()

    with ZipFile(file_object, "w") as zip_file:
        zip_file.writestr("roads.shp", b"dummy")
        zip_file.writestr("roads.dbf", b"dummy")

    file_object.seek(0)

    result = validate_shapefile_zip(file_object)

    assert result["valid"] is False
    assert ".shx" in result["message"]


def test_corrupted_zip_is_rejected():
    file_object = BytesIO(b"This is not a ZIP file.")

    result = validate_shapefile_zip(file_object)

    assert result["valid"] is False
    assert "invalid or corrupted" in result["message"]


def test_invalid_kml_xml_is_rejected():
    file_object = BytesIO(b"This is not valid XML")

    result = validate_kml(file_object)

    assert result["valid"] is False
    assert "invalid XML" in result["message"]