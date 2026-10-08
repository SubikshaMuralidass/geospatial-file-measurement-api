from pathlib import Path
from tempfile import NamedTemporaryFile, TemporaryDirectory
from zipfile import ZipFile

from fastapi import UploadFile


async def save_kml_to_temp(file: UploadFile) -> Path:
    temp_file = NamedTemporaryFile(delete=False, suffix=".kml")

    try:
        while chunk := await file.read(1024 * 1024):
            temp_file.write(chunk)
    finally:
        temp_file.close()

    return Path(temp_file.name)


async def save_shapefile_zip_to_temp(file: UploadFile) -> Path:
    temp_file = NamedTemporaryFile(delete=False, suffix=".zip")

    try:
        while chunk := await file.read(1024 * 1024):
            temp_file.write(chunk)
    finally:
        temp_file.close()

    return Path(temp_file.name)