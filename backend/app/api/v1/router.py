from fastapi import APIRouter

from app.api.v1 import auth, compare, documents, faq, qa, reports, streaming, summarize, system, users

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