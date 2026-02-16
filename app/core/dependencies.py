from functools import lru_cache

from app.core.config import settings
from app.core.minio import MinioService


@lru_cache
def get_minio_service():

    return MinioService(
        endpoint=settings.minio_endpoint,
        access_key=settings.minio_access_key,
        secret_key=settings.minio_secret_key,
        bucket_name=settings.minio_bucket,
        secure=settings.minio_secure,
    )