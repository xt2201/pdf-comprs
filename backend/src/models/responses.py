"""
Response Models

Pydantic models for API responses.
"""

from typing import Optional

from pydantic import BaseModel, Field


class CompressionConfigUsed(BaseModel):
    """Compression configuration that was used."""

    dpi: int
    quality: int
    description: str


class CompressionResponse(BaseModel):
    """Response for PDF compression operation."""

    success: bool
    job_id: str
    original_size_mb: float = Field(description="Original file size in MB")
    compressed_size_mb: float = Field(description="Compressed file size in MB")
    reduction_percent: float = Field(description="Size reduction percentage")
    config_used: Optional[CompressionConfigUsed] = None
    target_reached: bool = False
    download_url: str = Field(description="URL to download compressed PDF")
    message: str = ""


class ImageToPdfResponse(BaseModel):
    """Response for image to PDF conversion."""

    success: bool
    job_id: str
    pages: int = Field(description="Number of pages in PDF")
    original_size_mb: float = Field(description="Original combined size in MB")
    compressed_size_mb: float = Field(description="Final file size in MB")
    reduction_percent: float = Field(description="Size reduction percentage")
    download_url: str = Field(description="URL to download PDF")
    message: str = ""


class JobStatusResponse(BaseModel):
    """Response for job status check."""

    job_id: str
    status: str = Field(description="Job status: pending, processing, completed, failed")
    progress: int = Field(ge=0, le=100, description="Progress percentage")
    message: str = ""


class PresetItem(BaseModel):
    """Single compression preset."""

    name: str
    label: str
    dpi: int
    quality: int
    description: str = ""


class PresetsResponse(BaseModel):
    """Response for available presets."""

    presets: list[PresetItem]


class ErrorDetail(BaseModel):
    """Error detail information."""

    code: str
    message: str


class ErrorResponse(BaseModel):
    """Error response format."""

    success: bool = False
    error: ErrorDetail


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    version: str
    timestamp: str
