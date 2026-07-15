import boto3

from app.core.config import settings


def get_s3_client():
    """Return a configured boto3 S3 client using credentials from settings."""
    return boto3.client(
        "s3",
        aws_access_key_id=settings.aws_access_key_id,
        aws_secret_access_key=settings.aws_secret_access_key,
        region_name=settings.aws_region,
    )