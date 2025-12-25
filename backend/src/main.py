"""
FastAPI Main Application

Entry point for the PDF Compression Tool API.
"""

import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from src.api.routes import api_router
from src.config import get_config, get_config_dict
from src.logger import configure_logging, get_logger
from src.services.file_manager import get_file_manager
from src.utils.ngrok_tunnel import get_ngrok_tunnel

# Configure logging first
config_dict = get_config_dict()
configure_logging(config_dict)

logger = get_logger(__name__)


async def cleanup_task():
    """Background task for cleaning up old files."""
    config = get_config()
    file_manager = get_file_manager()
    interval = config.cleanup.interval_minutes * 60

    while True:
        await asyncio.sleep(interval)
        try:
            cleaned = file_manager.cleanup_old_jobs()
            if cleaned > 0:
                logger.info(f"Cleanup task: removed {cleaned} old jobs")
        except Exception as e:
            logger.error(f"Cleanup task error: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    config = get_config()

    logger.info(f"Starting {config.app.name} v{config.app.version}")

    # Start ngrok tunnel if enabled
    ngrok = get_ngrok_tunnel()
    if ngrok.is_enabled:
        public_url = ngrok.start(config.server.backend.port)
        if public_url:
            logger.info(f"Public URL: {public_url}")

    # Start cleanup background task
    cleanup_task_handle = None
    if config.cleanup.enabled:
        cleanup_task_handle = asyncio.create_task(cleanup_task())
        logger.info("Cleanup background task started")

    yield

    # Shutdown
    logger.info("Shutting down...")

    # Cancel cleanup task
    if cleanup_task_handle:
        cleanup_task_handle.cancel()
        try:
            await cleanup_task_handle
        except asyncio.CancelledError:
            pass

    # Stop ngrok tunnel
    ngrok.stop()

    logger.info("Shutdown complete")


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    config = get_config()

    app = FastAPI(
        title=config.app.name,
        description=config.app.description,
        version=config.app.version,
        lifespan=lifespan,
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
    )

    # Configure CORS
    cors_config = config.server.cors
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_config.allow_origins,
        allow_credentials=True,
        allow_methods=cors_config.allow_methods,
        allow_headers=cors_config.allow_headers,
    )

    # Include API routes
    app.include_router(api_router)

    logger.info("FastAPI application created")

    return app


# Create the application instance
app = create_app()


if __name__ == "__main__":
    import uvicorn

    config = get_config()
    server_config = config.server.backend

    uvicorn.run(
        "src.main:app",
        host=server_config.host,
        port=server_config.port,
        reload=server_config.reload,
        workers=server_config.workers if not server_config.reload else 1,
    )
