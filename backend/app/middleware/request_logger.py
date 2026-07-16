import time
import uuid

from fastapi import Request

from app.core.logging import get_logger

logger = get_logger("request")


async def log_requests(request: Request, call_next):
    """Log every incoming request with a unique ID, method, path, status, and duration."""
    request_id = str(uuid.uuid4())[:8]
    start_time = time.perf_counter()

    logger.info("[%s] --> %s %s", request_id, request.method, request.url.path)

    response = await call_next(request)

    duration_ms = (time.perf_counter() - start_time) * 1000
    logger.info(
        "[%s] <-- %s %s status=%d duration=%.1fms",
        request_id, request.method, request.url.path, response.status_code, duration_ms,
    )
    response.headers["X-Request-ID"] = request_id
    return response