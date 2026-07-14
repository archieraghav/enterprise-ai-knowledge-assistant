from fastapi import FastAPI

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.logging import configure_logging
from app.middleware.error_handler import register_exception_handlers

configure_logging()

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
)

register_exception_handlers(app)
app.include_router(api_router, prefix=settings.api_v1_prefix)