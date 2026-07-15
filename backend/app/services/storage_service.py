import uuid

from botocore.exceptions import ClientError

from app.core.aws import get_s3_client
from app.core.config import settings
from app.core.exceptions import AppException
from app.core.logging import get_logger

logger = get_logger(__name__)


def build_file_key(organization_id: uuid.UUID, filename: str) -> str:
    """Construct a unique, namespaced S3 object key for an uploaded file."""
    unique_id = uuid.uuid4().hex
    return f"organizations/{organization_id}/documents/{unique_id}_{filename}"


def upload_file(file_key: str, file_bytes: bytes, content_type: str) -> None:
    """Upload raw file bytes to S3 under the given key."""
    client = get_s3_client()
    try:
        client.put_object(
            Bucket=settings.s3_bucket_name,
            Key=file_key,
            Body=file_bytes,
            ContentType=content_type,
        )
    except ClientError as exc:
        logger.exception("Failed to upload file to S3: %s", file_key)
        raise AppException("Failed to upload file to storage", status_code=502) from exc


def generate_presigned_download_url(file_key: str, expires_in_seconds: int = 3600) -> str:
    """Generate a temporary signed URL to download a private S3 object."""
    client = get_s3_client()
    try:
        return client.generate_presigned_url(
            "get_object",
            Params={"Bucket": settings.s3_bucket_name, "Key": file_key},
            ExpiresIn=expires_in_seconds,
        )
    except ClientError as exc:
        logger.exception("Failed to generate presigned URL for: %s", file_key)
        raise AppException("Failed to generate download link", status_code=502) from exc


def delete_file(file_key: str) -> None:
    """Delete a file from S3."""
    client = get_s3_client()
    try:
        client.delete_object(Bucket=settings.s3_bucket_name, Key=file_key)
    except ClientError as exc:
        logger.exception("Failed to delete file from S3: %s", file_key)
        raise AppException("Failed to delete file from storage", status_code=502) from exc