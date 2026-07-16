from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.api.v1.router import api_router
from app.core.cloudwatch import configure_cloudwatch_logging
from app.core.config import settings
from app.core.logging import configure_logging
from app.middleware.error_handler import register_exception_handlers
from app.middleware.rate_limiter import limiter
from app.middleware.request_logger import log_requests

configure_logging()
configure_cloudwatch_logging()

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.middleware("http")(log_requests)

register_exception_handlers(app)
app.include_router(api_router, prefix=settings.api_v1_prefix)