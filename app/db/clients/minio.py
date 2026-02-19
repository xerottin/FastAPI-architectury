import io
import uuid
from datetime import timedelta

from minio import Minio
from minio.error import S3Error
from fastapi import UploadFile, HTTPException

from core.exceptions import AppException


class MinioService:

    ALLOWED_CONTENT_TYPES = {
        "image/jpeg",
        "image/png",
        "image/webp",
        "image/gif",
        "image/svg+xml",
    }
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

    def __init__(
        self,
        endpoint: str,
        access_key: str,
        secret_key: str,
        bucket_name: str = "photos",
        secure: bool = False,
        public_url: str | None = None,
    ):
        self.client = Minio(
            endpoint=endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=secure,
        )
        self.bucket_name = bucket_name

        if public_url:
            from urllib.parse import urlparse

            parsed = urlparse(public_url)
            public_secure = parsed.scheme == "https"
            public_endpoint = parsed.netloc  # e.g. "minio.example.com" or "localhost:9222"
            self._presign_client = Minio(
                endpoint=public_endpoint,
                access_key=access_key,
                secret_key=secret_key,
                secure=public_secure,
                region="us-east-1",  # prevents network call to discover region
            )
        else:
            self._presign_client = self.client

        self._ensure_bucket()

    def _ensure_bucket(self) -> None:
        """Create the bucket if it doesn't exist."""
        if not self.client.bucket_exists(self.bucket_name):
            self.client.make_bucket(self.bucket_name)
            # Set bucket policy to allow public read (optional)
            # self._set_public_read_policy()

    def _validate_file(self, file: UploadFile) -> None:
        """Validate file type and size."""
        if file.content_type not in self.ALLOWED_CONTENT_TYPES:
            raise AppException(
                code="file_type_not_allowed",
                i18n_key="denied.file_type_not_allowed",
                status_code=400,
                detail=f"File type '{file.content_type}' not allowed. "
                       f"Allowed: {', '.join(self.ALLOWED_CONTENT_TYPES)}",
            )

    def _generate_object_name(self, filename: str, prefix: str = "") -> str:
        ext = filename.rsplit(".", 1)[-1] if "." in filename else "jpg"
        unique_name = f"{uuid.uuid4().hex}.{ext}"
        return f"{prefix}/{unique_name}" if prefix else unique_name

    async def upload_file(
        self,
        file: UploadFile,
        prefix: str = "",
        custom_name: str | None = None,
    ) -> dict:
        self._validate_file(file)

        content = await file.read()
        file_size = len(content)

        if file_size > self.MAX_FILE_SIZE:
            raise AppException(
                code="domain_not_found",
                i18n_key="errors.domain_not_found",
                status_code=404,
                detail=f"File too large ({file_size} bytes). Max: {self.MAX_FILE_SIZE} bytes.",
            )

        object_name = custom_name or self._generate_object_name(
            file.filename or "upload.jpg", prefix
        )

        try:
            self.client.put_object(
                bucket_name=self.bucket_name,
                object_name=object_name,
                data=io.BytesIO(content),
                length=file_size,
                content_type=file.content_type,
            )
        except S3Error as e:
            raise AppException(
                code="minio_server_error",
                i18n_key="errors.minio_server_error",
                status_code=500,
                detail=f"minio_server_error error: {e}",
            )

        return {
            "object_name": object_name,
            "bucket": self.bucket_name,
            "size": file_size,
            "content_type": file.content_type,
            "url": self.get_presigned_url(object_name),
        }

    async def upload_bytes(
        self,
        data: bytes,
        filename: str,
        content_type: str = "image/jpeg",
        prefix: str = "",
    ) -> dict:
        """Upload raw bytes to MinIO."""
        object_name = self._generate_object_name(filename, prefix)

        try:
            self.client.put_object(
                bucket_name=self.bucket_name,
                object_name=object_name,
                data=io.BytesIO(data),
                length=len(data),
                content_type=content_type,
            )
        except S3Error as e:
            raise AppException(
                code="minio_server_error",
                i18n_key="errors.minio_server_error",
                status_code=500,
                detail=f"minio_server_error error: {e}",
            )

        return {
            "object_name": object_name,
            "bucket": self.bucket_name,
            "size": len(data),
            "content_type": content_type,
            "url": self.get_presigned_url(object_name),
        }

    def get_presigned_url(
        self, object_name: str, expires: timedelta = timedelta(hours=1)
    ) -> str:
        """Generate a presigned URL for downloading/viewing a file."""
        try:
            return self._presign_client.presigned_get_object(
                self.bucket_name, object_name, expires=expires
            )
        except S3Error as e:
            raise AppException(
                code="minio_server_error",
                i18n_key="errors.minio_server_error",
                status_code=500,
                detail=f"minio_server_error error: {e}",
            )

    def get_upload_presigned_url(
        self, object_name: str, expires: timedelta = timedelta(hours=1)
    ) -> str:
        """Generate a presigned URL for direct client-side upload."""
        try:
            return self._presign_client.presigned_put_object(
                self.bucket_name, object_name, expires=expires
            )
        except S3Error as e:
            raise AppException(
                code="minio_server_error",
                i18n_key="errors.minio_server_error",
                status_code=500,
                detail=f"minio_server_error error: {e}",
            )

    def download_file(self, object_name: str) -> bytes:
        """Download a file from MinIO and return its bytes."""
        try:
            response = self.client.get_object(self.bucket_name, object_name)
            return response.read()
        except S3Error as e:
            if e.code == "NoSuchKey":
                raise HTTPException(status_code=404, detail="File not found.")
            raise HTTPException(status_code=500, detail=f"MinIO download failed: {e}")
        finally:
            response.close()
            response.release_conn()

    def delete_file(self, object_name: str) -> bool:
        """Delete a file from MinIO."""
        try:
            self.client.remove_object(self.bucket_name, object_name)
            return True
        except S3Error as e:
            raise AppException(
                code="minio_server_error",
                i18n_key="errors.minio_server_error",
                status_code=500,
                detail=f"minio_server_error error: {e}",
            )

    def delete_files(self, object_names: list[str]) -> None:
        """Delete multiple files from MinIO."""
        from minio.deleteobjects import DeleteObject

        delete_objects = [DeleteObject(name) for name in object_names]
        errors = self.client.remove_objects(self.bucket_name, delete_objects)
        for error in errors:
            raise AppException(
                code="failed_to_delete_objects",
                i18n_key="errors.failed_to_delete_objects",
                status_code=500,
                detail=f"Failed to delete {error.name}: {error.message}",
            )

    def file_exists(self, object_name: str) -> bool:
        """Check if a file exists in the bucket."""
        try:
            self.client.stat_object(self.bucket_name, object_name)
            return True
        except S3Error:
            return False

    def list_files(self, prefix: str = "", recursive: bool = True) -> list[dict]:
        """List files in the bucket with optional prefix filter."""
        objects = self.client.list_objects(
            self.bucket_name, prefix=prefix, recursive=recursive
        )
        return [
            {
                "object_name": obj.object_name,
                "size": obj.size,
                "last_modified": obj.last_modified,
                "content_type": obj.content_type,
            }
            for obj in objects
        ]
