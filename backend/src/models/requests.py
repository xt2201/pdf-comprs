"""
Request Models

Pydantic models for API request validation.
"""

from pydantic import BaseModel, Field


class CompressionSettings(BaseModel):
    """Compression settings for PDF operations."""

    target_size_mb: float = Field(
        default=0.5,
        ge=0.1,
        le=100.0,
        description="Target file size in MB",
    )
    dpi: int = Field(
        default=72,
        ge=10,
        le=300,
        description="Image resolution (DPI)",
    )
    quality: int = Field(
        default=50,
        ge=5,
        le=100,
        description="JPEG quality (0-100)",
    )
    auto_compress: bool = Field(
        default=True,
        description="Automatically find best compression settings",
    )
    output_filename: str = Field(
        default="compressed",
        max_length=255,
        description="Output filename (without extension)",
    )


class ImageToPdfSettings(BaseModel):
    """Settings for image to PDF conversion."""

    target_size_mb: float = Field(
        default=0.5,
        ge=0.1,
        le=100.0,
        description="Target file size in MB",
    )
    dpi: int = Field(
        default=72,
        ge=10,
        le=300,
        description="Image resolution (DPI)",
    )
    quality: int = Field(
        default=50,
        ge=5,
        le=100,
        description="JPEG quality (0-100)",
    )
    auto_compress: bool = Field(
        default=True,
        description="Automatically compress after PDF creation",
    )
    output_filename: str = Field(
        default="output",
        max_length=255,
        description="Output filename (without extension)",
    )
