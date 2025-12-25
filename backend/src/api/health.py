"""
Health Check Endpoint
"""

from datetime import datetime, timezone

from fastapi import APIRouter

from src.config import get_config
from src.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.get("/health")
async def health_check():
    """Check API health status."""
    config = get_config()
    logger.debug("Health check requested")

    return {
        "status": "healthy",
        "version": config.app.version,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
