"""
API Router Configuration
"""

from fastapi import APIRouter

from src.api.compression import router as compression_router
from src.api.config import router as config_router
from src.api.health import router as health_router

# Create main API router
api_router = APIRouter(prefix="/api")

# Include sub-routers
api_router.include_router(health_router)
api_router.include_router(config_router)
api_router.include_router(compression_router)
