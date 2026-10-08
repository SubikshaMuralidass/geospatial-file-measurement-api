from pathlib import Path
from zipfile import BadZipFile, ZipFile
from xml.etree import ElementTree


MAX_SHAPEFILE_ZIP_SIZE = 2 * 1024 * 1024 * 1024  # 2 GB


def validate_file(filename: str, file_size: int | None = None) -> dict:
    """
    Validate the uploaded file based on its filename and size.

    KML:
        - No 2 GB restriction.

    Shapefile:
        - Must be a ZIP file.
        - Must be strictly smaller than 2 GB.
    """

    extension = Path(filename).suffix.lower()

    if extension == ".kml":
        return {
            "valid": True,
            "file_type": "kml",
            "message": "KML file accepted.",
        }

    if extension == ".zip":
        if file_size is not None and file_size > MAX_SHAPEFILE_ZIP_SIZE:
            return {
                "valid": False,
                "file_type": "shapefile",
                "message": (
                    "Please upload either a KML file or a "
                    "Shapefile ZIP file less than 2 GB."
                ),
            }

        return {
            "valid": True,
            "file_type": "shapefile",
            "message": "Shapefile ZIP accepted.",
        }

    return {
        "valid": False,
        "file_type": None,
        "message": (
            "Please upload either a KML file or a "
            "Shapefile ZIP file less than 2 GB."
        ),
    }

def validate_shapefile_zip(file) -> dict:
    """
    Verify that the uploaded ZIP is a valid Shapefile archive.
    """

    try:
        with ZipFile(file) as zip_file:
            files = {
                Path(name).suffix.lower()
                for name in zip_file.namelist()
                if not name.endswith("/")
            }

            required_files = {".shp", ".shx", ".dbf"}

            if not required_files.issubset(files):
                return {
                    "valid": False,
                    "message": (
                        "Invalid Shapefile ZIP. "
                        "The ZIP must contain .shp, .shx, and .dbf files."
                    ),
                }

    except BadZipFile:
        return {
            "valid": False,
            "message": "The uploaded ZIP file is invalid or corrupted.",
        }

    return {
        "valid": True,
        "message": "Valid Shapefile ZIP.",
    }

def validate_kml(file) -> dict:
    """
    Verify that the uploaded file is valid KML/XML.
    """

    try:
        file.seek(0)

        root = ElementTree.parse(file).getroot()

        if not root.tag.lower().endswith("kml"):
            return {
                "valid": False,
                "message": "The uploaded file is not a valid KML file.",
            }

    except ElementTree.ParseError:
        return {
            "valid": False,
            "message": "The uploaded KML file contains invalid XML.",
        }

    finally:
        file.seek(0)

    return {
        "valid": True,
        "message": "Valid KML file.",
    }