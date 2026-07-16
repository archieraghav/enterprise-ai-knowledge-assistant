import logging

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


def configure_cloudwatch_logging() -> None:
    """Attach a CloudWatch log handler to the root logger, if enabled.

    This is opt-in via ENABLE_CLOUDWATCH_LOGGING — in local development
    this does nothing, keeping logs purely local. In a real AWS deployment
    (Day 60), setting this to true would ship logs to CloudWatch for
    centralized monitoring.
    """
    if not settings.enable_cloudwatch_logging:
        logger.info("CloudWatch logging disabled (local development mode)")
        return

    try:
        import watchtower

        cloudwatch_handler = watchtower.CloudWatchLogHandler(
            log_group=settings.cloudwatch_log_group,
            stream_name=settings.cloudwatch_log_stream,
        )
        logging.getLogger().addHandler(cloudwatch_handler)
        logger.info("CloudWatch logging enabled: group=%s stream=%s",
                    settings.cloudwatch_log_group, settings.cloudwatch_log_stream)
    except Exception:
        logger.exception("Failed to configure CloudWatch logging — continuing with local logs only")