import uuid

from fastapi import APIRouter, File, UploadFile

from app.models.file_record import FileRecord
from app.models.store import files_store

from app.services.file_storage import save_kml_to_temp
from app.services.geospatial import read_kml, extract_measurements

from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile

from app.services.file_storage import (
    save_kml_to_temp,
    save_shapefile_zip_to_temp,
)

from app.services.geospatial import (
    read_kml,
    read_shapefile,
    extract_measurements,
)

from app.services.file_validator import (
    validate_file,
    validate_shapefile_zip,
    validate_kml,
)

router = APIRouter(
    prefix="/api/files",
    tags=["Files"],
)

@router.post("/")
async def upload_file(file: UploadFile = File(...)):
    file_size = None

    if file.filename.lower().endswith(".zip"):
        file.file.seek(0, 2)
        file_size = file.file.tell()
        file.file.seek(0)

    # Step 1: filename + size validation
    validation = validate_file(
        filename=file.filename,
        file_size=file_size,
    )

    if not validation["valid"]:
        return validation

    # Step 2: actual ZIP/Shapefile validation
    if validation["file_type"] == "shapefile":
        shapefile_validation = validate_shapefile_zip(file.file)

        if not shapefile_validation["valid"]:
            return shapefile_validation

        file.file.seek(0)  # IMPORTANT

        temp_zip_path = await save_shapefile_zip_to_temp(file)

        try:
            with TemporaryDirectory() as extract_dir:
                with ZipFile(temp_zip_path, "r") as zip_file:
                    zip_file.extractall(extract_dir)

                shp_files = list(Path(extract_dir).rglob("*.shp"))

                if not shp_files:
                    return {
                        "valid": False,
                        "message": "No .shp file found in the Shapefile ZIP."
                    }

                shp_path = shp_files[0]

                gdf = read_shapefile(str(shp_path))
                measurements = extract_measurements(gdf)

                file_id = str(uuid.uuid4())

                record = FileRecord(
                    id=file_id,
                    filename=file.filename,
                    feature_count=len(gdf),
                    crs=gdf.crs.to_string() if gdf.crs else None,
                    status="COMPLETED",
                    measurements=measurements,
                )

                files_store[file_id] = record

                return {
                    "id": file_id,
                    "filename": file.filename,
                    "feature_count": len(gdf),
                    "crs": gdf.crs.to_string() if gdf.crs else None,
                    "status": "COMPLETED",
                }

        finally:
            temp_zip_path.unlink(missing_ok=True)

    # Step 3: actual KML validation
    if validation["file_type"] == "kml":
        kml_validation = validate_kml(file.file)

        if not kml_validation["valid"]:
            return kml_validation

        # Save KML temporarily
        temp_path = await save_kml_to_temp(file)

        try:
            # Read KML using GeoPandas
            gdf = read_kml(str(temp_path))

            # Extract measurements
            measurements = extract_measurements(gdf)

            # Generate unique ID
            file_id = str(uuid.uuid4())

            # Create in-memory record
            record = FileRecord(
                id=file_id,
                filename=file.filename,
                feature_count=len(gdf),
                crs=gdf.crs.to_string() if gdf.crs else None,
                status="COMPLETED",
                measurements=measurements,
            )

            # Store record
            files_store[file_id] = record

            return {
                "id": file_id,
                "filename": file.filename,
                "feature_count": len(gdf),
                "crs": gdf.crs.to_string() if gdf.crs else None,
                "status": "COMPLETED",
            }

        finally:
            # Delete temporary file
            temp_path.unlink(missing_ok=True)

            
@router.get("/{file_id}")
async def get_file(file_id: str):
    record = files_store.get(file_id)

    if record is None:
        return {
            "message": "File not found."
        }

    return {
        "id": record.id,
        "filename": record.filename,
        "feature_count": record.feature_count,
        "crs": record.crs,
        "status": record.status,
    }


@router.get("/{file_id}/measurements")
async def get_measurements(file_id: str):
    record = files_store.get(file_id)

    if record is None:
        return {
            "message": "File not found."
        }

    return {
        "id": record.id,
        "filename": record.filename,
        "measurements": record.measurements,
    }