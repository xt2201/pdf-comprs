"""
Config Endpoint

Endpoint to expose app configuration to frontend.
"""

from fastapi import APIRouter
from pydantic import BaseModel

from src.config import get_config
from src.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


class AppInfoResponse(BaseModel):
    """Application information response."""

    name: str
    title: str
    version: str
    description: str
    logo_url: str


@router.get("/app-info", response_model=AppInfoResponse)
async def get_app_info():
    """Get application information for frontend."""
    config = get_config()
    logger.debug("App info requested")

    return AppInfoResponse(
        name=config.app.name,
        title=config.ui.title,
        version=config.app.version,
        description=config.app.description,
        logo_url=config.ui.logo_url,
    )
