from fastapi import APIRouter, Depends, UploadFile, File, Query
from fastapi.responses import StreamingResponse
import io

from core.dependencies import get_minio_service
from core.minio import MinioService

router = APIRouter()


@router.post("/upload")
async def upload_photo(
    file: UploadFile = File(...),
    prefix: str = Query("", description="Subfolder prefix, e.g. 'avatars'"),
    minio: "MinioService" = Depends(get_minio_service),
):
    result = await minio.upload_file(file, prefix=prefix)
    return result


@router.post("/upload/multiple")
async def upload_multiple_photos(
    files: list[UploadFile] = File(...),
    prefix: str = Query("", description="Subfolder prefix"),
    minio: "MinioService" = Depends(get_minio_service),
):
    results = []
    for file in files:
        result = await minio.upload_file(file, prefix=prefix)
        results.append(result)
    return results

@router.get("/")
def list_photos(
    prefix: str = Query("", description="Filter by prefix"),
    minio: "MinioService" = Depends(get_minio_service),
):
    return minio.list_files(prefix=prefix)

@router.get("/download/{object_name:path}")
def download_photo(
    object_name: str,
    minio: "MinioService" = Depends(get_minio_service),
):
    data = minio.download_file(object_name)
    return StreamingResponse(io.BytesIO(data), media_type="image/jpeg")


@router.get("/url/{object_name:path}")
def get_photo_url(
    object_name: str,
    minio: "MinioService" = Depends(get_minio_service),
):
    return {"url": minio.get_presigned_url(object_name)}


@router.delete("/{object_name:path}")
def delete_photo(
    object_name: str,
    minio: "MinioService" = Depends(get_minio_service),
):
    minio.delete_file(object_name)
    return {"detail": "Deleted", "object_name": object_name}
