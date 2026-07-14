import json

import boto3
from botocore.exceptions import ClientError

from app.core.logging import get_logger

logger = get_logger(__name__)


def get_secret(secret_name: str, region_name: str = "us-east-1") -> dict[str, str] | None:
    """Fetch a JSON secret from AWS Secrets Manager.

    Returns None if the secret cannot be retrieved (e.g. no AWS credentials
    configured locally), allowing callers to fall back to .env values.
    """
    session = boto3.session.Session()
    client = session.client(service_name="secretsmanager", region_name=region_name)

    try:
        response = client.get_secret_value(SecretId=secret_name)
    except ClientError as exc:
        logger.warning("Could not retrieve secret '%s': %s", secret_name, exc)
        return None

    secret_string = response.get("SecretString")
    if secret_string is None:
        return None

    return json.loads(secret_string)