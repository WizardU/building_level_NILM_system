from fastapi import APIRouter

from app.routers import (
    analytics,
    appliances,
    auth,
    buildings,
    disaggregation,
    events,
    measurements,
    meters,
)

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth.router)
api_router.include_router(buildings.router)
api_router.include_router(meters.router)
api_router.include_router(measurements.router)
api_router.include_router(events.router)
api_router.include_router(disaggregation.router)
api_router.include_router(appliances.router)
api_router.include_router(analytics.router)
