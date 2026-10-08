from fastapi import FastAPI

from app.api.files import router as files_router


app = FastAPI(
    title="Geospatial File Measurement API",
    description="Backend API for processing KML and Shapefile files.",
    version="1.0.0",
)

app.include_router(files_router)


@app.get("/")
def root():
    return {
        "message": "Geospatial File Measurement API is running"
    }
# from pathlib import Path

# from fastapi import FastAPI, File, HTTPException, UploadFile

# app = FastAPI(
#     title="Geospatial File Measurement API",
#     description="Backend API for processing KML and Shapefile files.",
#     version="1.0.0",
# )

# MAX_SHAPEFILE_ZIP_SIZE = 2 * 1024 * 1024 * 1024  # 2 GB


# @app.get("/")
# def root():
#     return {
#         "message": "Geospatial File Measurement API is running"
#     }


# @app.post("/api/files/")
# async def upload_file(file: UploadFile = File(...)):
#     filename = file.filename or ""
#     extension = Path(filename).suffix.lower()

#     # KML files: accepted regardless of size
#     if extension == ".kml":
#         return {
#             "filename": filename,
#             "type": "kml",
#             "message": "KML file accepted",
#         }

#     # Shapefile ZIP: must be below 2 GB
#     if extension == ".zip":
#         if file.size is not None and file.size >= MAX_SHAPEFILE_ZIP_SIZE:
#             raise HTTPException(
#                 status_code=413,
#                 detail="Shapefile ZIP must be less than 2 GB.",
#             )

#         return {
#             "filename": filename,
#             "type": "shapefile_zip",
#             "message": "Shapefile ZIP accepted",
#         }

#     # Everything else
#     raise HTTPException(
#         status_code=400,
#         detail=(
#             "Please upload either a KML file or a "
#             "Shapefile ZIP file less than 2 GB."
#         ),
#     )