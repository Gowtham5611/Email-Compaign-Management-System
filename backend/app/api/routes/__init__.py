from fastapi import APIRouter
from app.api.routes import auth, templates, recipients, campaigns, settings, dashboard

api_router = APIRouter(prefix="/api")
api_router.include_router(auth.router)
api_router.include_router(templates.router)
api_router.include_router(recipients.router)
api_router.include_router(campaigns.router)
api_router.include_router(settings.router)
api_router.include_router(dashboard.router)

