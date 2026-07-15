from fastapi import APIRouter

from app.api.v1 import (
    admin,
    auth,
    compare,
    documents,
    faq,
    feedback,
    qa,
    reports,
    search,
    streaming,
    summarize,
    system,
    users,
)

api_router = APIRouter()
api_router.include_router(system.router)
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(documents.router)
api_router.include_router(qa.router)
api_router.include_router(streaming.router)
api_router.include_router(summarize.router)
api_router.include_router(compare.router)
api_router.include_router(reports.router)
api_router.include_router(faq.router)
api_router.include_router(search.router)
api_router.include_router(admin.router)
api_router.include_router(feedback.router)