from fastapi import APIRouter
from app.api.v1.endpoints import (
    admin,
    analytics,
    auth,
    countries,
    etl,
    forecasts,
    health,
    hospitalizations,
    kpis,
    powerbi,
    testing,
    vaccinations,
)

api_router = APIRouter()

api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(countries.router, prefix="/countries", tags=["countries"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(vaccinations.router, prefix="/vaccinations", tags=["vaccinations"])
api_router.include_router(testing.router, prefix="/testing", tags=["testing"])
api_router.include_router(
    hospitalizations.router, prefix="/hospitalizations", tags=["hospitalizations"]
)
api_router.include_router(forecasts.router, prefix="/forecasts", tags=["forecasts"])
api_router.include_router(kpis.router, prefix="/kpis", tags=["kpis"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(etl.router, prefix="/etl", tags=["etl"])
api_router.include_router(powerbi.router, prefix="/powerbi", tags=["powerbi"])
