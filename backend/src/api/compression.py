"""
Compression API Endpoints
"""

import os
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse

from src.config import get_config
from src.logger import get_logger
from src.models.responses import (
    CompressionConfigUsed,
    CompressionResponse,
    ErrorDetail,
    ErrorResponse,
    ImageToPdfResponse,
    JobStatusResponse,
    PresetItem,
    PresetsResponse,
)
from src.services.file_manager import get_file_manager
from src.services.image_converter import get_image_converter
from src.services.pdf_compressor import get_pdf_compressor

logger = get_logger(__name__)
router = APIRouter(prefix="/compress", tags=["compression"])


def sanitize_filename(filename: str) -> str:
    """Sanitize filename to prevent path traversal and invalid characters."""
    # Remove path separators and null bytes
    filename = filename.replace("/", "").replace("\\", "").replace("\x00", "")
    # Remove leading dots
    while filename.startswith("."):
        filename = filename[1:]
    # Keep only alphanumeric, spaces, dashes, underscores
    sanitized = "".join(
        c for c in filename if c.isalnum() or c in (" ", "-", "_")
    ).strip()
    return sanitized or "output"


@router.post("/pdf", response_model=CompressionResponse)
async def compress_pdf(
    file: UploadFile = File(..., description="PDF file to compress"),
    target_size_mb: float = Form(default=0.5, ge=0.1, le=100.0),
    dpi: int = Form(default=72, ge=10, le=300),
    quality: int = Form(default=50, ge=5, le=100),
    auto_compress: bool = Form(default=True),
    output_filename: str = Form(default="compressed"),
):
    """
    Compress an existing PDF file.

    - **file**: PDF file to compress
    - **target_size_mb**: Target file size in MB (for auto mode)
    - **dpi**: Image resolution (lower = smaller file)
    - **quality**: JPEG quality 0-100 (lower = smaller file)
    - **auto_compress**: Automatically find best settings to reach target size
    - **output_filename**: Name for the output file
    """
    config = get_config()
    file_manager = get_file_manager()
    compressor = get_pdf_compressor()

    # Validate file type
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail={"code": "INVALID_FILE_TYPE", "message": "Only PDF files are allowed"},
        )

    # Check file size
    content = await file.read()
    file_size_mb = len(content) / (1024 * 1024)

    if file_size_mb > config.upload.max_file_size_mb:
        raise HTTPException(
            status_code=413,
            detail={
                "code": "FILE_TOO_LARGE",
                "message": f"File exceeds maximum size of {config.upload.max_file_size_mb} MB",
            },
        )

    logger.info(f"Received PDF for compression: {file.filename} ({file_size_mb:.2f} MB)")

    # Create job and save file
    job = file_manager.create_job(original_filename=file.filename)
    input_path = file_manager.save_uploaded_file(job.job_id, content, "input.pdf")

    # Sanitize output filename
    output_name = sanitize_filename(output_filename)
    output_path = file_manager.get_job_file_path(job.job_id, f"{output_name}.pdf")

    # Update job status
    file_manager.update_job(job.job_id, status="processing", progress=10)

    try:
        if auto_compress:
            result = compressor.compress_to_target_size(input_path, output_path, target_size_mb)
        else:
            success, msg = compressor.compress_with_settings(input_path, output_path, dpi, quality)
            if success:
                final_size = compressor.get_file_size_mb(output_path)
                reduction = ((file_size_mb - final_size) / file_size_mb) * 100
                result = type(
                    "Result",
                    (),
                    {
                        "success": True,
                        "initial_size_mb": file_size_mb,
                        "final_size_mb": final_size,
                        "reduction_percent": reduction,
                        "config_used": (dpi, quality, "Custom"),
                        "output_path": output_path,
                        "target_reached": final_size <= target_size_mb,
                    },
                )()
            else:
                result = type(
                    "Result",
                    (),
                    {
                        "success": False,
                        "error": msg,
                        "initial_size_mb": file_size_mb,
                        "final_size_mb": 0,
                        "reduction_percent": 0,
                    },
                )()

        if result.success:
            file_manager.update_job(
                job.job_id,
                status="completed",
                progress=100,
                output_file=output_path,
                message="Compression successful",
            )

            config_used = None
            if hasattr(result, "config_used") and result.config_used:
                dpi_used, qual_used, desc = result.config_used
                config_used = CompressionConfigUsed(
                    dpi=dpi_used, quality=qual_used, description=desc
                )

            return CompressionResponse(
                success=True,
                job_id=job.job_id,
                original_size_mb=round(result.initial_size_mb, 2),
                compressed_size_mb=round(result.final_size_mb, 2),
                reduction_percent=round(result.reduction_percent, 1),
                config_used=config_used,
                target_reached=getattr(result, "target_reached", False),
                download_url=f"/api/compress/download/{job.job_id}",
                message="PDF compressed successfully",
            )
        else:
            file_manager.update_job(job.job_id, status="failed", message=str(result.error))
            raise HTTPException(
                status_code=500,
                detail={
                    "code": "COMPRESSION_FAILED",
                    "message": str(result.error),
                },
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Compression error: {e}", exc_info=True)
        file_manager.update_job(job.job_id, status="failed", message=str(e))
        raise HTTPException(
            status_code=500,
            detail={"code": "COMPRESSION_FAILED", "message": str(e)},
        )


@router.post("/images-to-pdf", response_model=ImageToPdfResponse)
async def images_to_pdf(
    files: list[UploadFile] = File(..., description="Image files to convert"),
    target_size_mb: float = Form(default=0.5, ge=0.1, le=100.0),
    dpi: int = Form(default=72, ge=10, le=300),
    quality: int = Form(default=50, ge=5, le=100),
    auto_compress: bool = Form(default=True),
    output_filename: str = Form(default="output"),
):
    """
    Convert images to PDF and optionally compress.

    - **files**: Image files in desired page order
    - **target_size_mb**: Target file size in MB
    - **auto_compress**: Compress the PDF after creation
    - **output_filename**: Name for the output file
    """
    config = get_config()
    file_manager = get_file_manager()
    converter = get_image_converter()
    compressor = get_pdf_compressor()

    if not files:
        raise HTTPException(
            status_code=400,
            detail={"code": "NO_FILES", "message": "No image files provided"},
        )

    # Validate and save files
    job = file_manager.create_job(original_filename="images")
    image_paths = []
    total_size = 0

    allowed_extensions = set(config.upload.allowed_image_types)

    for i, upload_file in enumerate(files):
        if not upload_file.filename:
            continue

        ext = Path(upload_file.filename).suffix.lower()
        if ext not in allowed_extensions:
            logger.warning(f"Skipping unsupported file: {upload_file.filename}")
            continue

        content = await upload_file.read()
        total_size += len(content)

        # Check total size
        if total_size / (1024 * 1024) > config.upload.max_file_size_mb:
            file_manager.cleanup_job(job.job_id)
            raise HTTPException(
                status_code=413,
                detail={
                    "code": "FILE_TOO_LARGE",
                    "message": f"Total size exceeds maximum of {config.upload.max_file_size_mb} MB",
                },
            )

        # Save with index prefix to preserve order
        safe_filename = f"{i:03d}_{sanitize_filename(Path(upload_file.filename).stem)}{ext}"
        file_path = file_manager.save_uploaded_file(job.job_id, content, safe_filename)
        image_paths.append(file_path)

    if not image_paths:
        file_manager.cleanup_job(job.job_id)
        raise HTTPException(
            status_code=400,
            detail={"code": "NO_VALID_IMAGES", "message": "No valid image files found"},
        )

    logger.info(f"Converting {len(image_paths)} images to PDF")

    # Update job status
    file_manager.update_job(job.job_id, status="processing", progress=20)

    # Sanitize output filename
    output_name = sanitize_filename(output_filename)
    temp_pdf_path = file_manager.get_job_file_path(job.job_id, f"{output_name}_temp.pdf")
    final_pdf_path = file_manager.get_job_file_path(job.job_id, f"{output_name}.pdf")

    try:
        # Convert images to PDF
        conversion_result = converter.convert_images_to_pdf(image_paths, temp_pdf_path)

        if not conversion_result.success:
            file_manager.update_job(job.job_id, status="failed", message=conversion_result.error)
            raise HTTPException(
                status_code=500,
                detail={"code": "CONVERSION_FAILED", "message": conversion_result.error},
            )

        file_manager.update_job(job.job_id, progress=50)

        initial_size = conversion_result.size_mb
        final_size = initial_size
        reduction = 0.0

        # Compress if needed
        if auto_compress and initial_size > target_size_mb:
            file_manager.update_job(job.job_id, progress=60, message="Compressing PDF...")
            result = compressor.compress_to_target_size(temp_pdf_path, final_pdf_path, target_size_mb)
            if result.success:
                final_size = result.final_size_mb
                reduction = result.reduction_percent
                # Clean up temp PDF
                if os.path.exists(temp_pdf_path):
                    os.unlink(temp_pdf_path)
            else:
                # Use uncompressed version
                os.rename(temp_pdf_path, final_pdf_path)
        else:
            # No compression needed
            os.rename(temp_pdf_path, final_pdf_path)

        file_manager.update_job(
            job.job_id,
            status="completed",
            progress=100,
            output_file=final_pdf_path,
            message="PDF created successfully",
        )

        return ImageToPdfResponse(
            success=True,
            job_id=job.job_id,
            pages=conversion_result.page_count,
            original_size_mb=round(initial_size, 2),
            compressed_size_mb=round(final_size, 2),
            reduction_percent=round(reduction, 1),
            download_url=f"/api/compress/download/{job.job_id}",
            message="PDF created successfully",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Image to PDF error: {e}", exc_info=True)
        file_manager.update_job(job.job_id, status="failed", message=str(e))
        raise HTTPException(
            status_code=500,
            detail={"code": "CONVERSION_FAILED", "message": str(e)},
        )


@router.get("/status/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str):
    """Get the status of a compression job."""
    file_manager = get_file_manager()
    job = file_manager.get_job(job_id)

    if not job:
        raise HTTPException(
            status_code=404,
            detail={"code": "JOB_NOT_FOUND", "message": f"Job not found: {job_id}"},
        )

    return JobStatusResponse(
        job_id=job.job_id,
        status=job.status,
        progress=job.progress,
        message=job.message,
    )


@router.get("/download/{job_id}")
async def download_file(job_id: str):
    """Download the compressed PDF file."""
    file_manager = get_file_manager()
    output_file = file_manager.get_output_file(job_id)

    if not output_file:
        raise HTTPException(
            status_code=404,
            detail={"code": "FILE_NOT_FOUND", "message": "Output file not found"},
        )

    filename = Path(output_file).name
    return FileResponse(
        path=output_file,
        media_type="application/pdf",
        filename=filename,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/preview/{job_id}")
async def preview_file(job_id: str):
    """Preview the compressed PDF file in browser."""
    file_manager = get_file_manager()
    output_file = file_manager.get_output_file(job_id)

    if not output_file:
        raise HTTPException(
            status_code=404,
            detail={"code": "FILE_NOT_FOUND", "message": "Output file not found"},
        )

    filename = Path(output_file).name
    return FileResponse(
        path=output_file,
        media_type="application/pdf",
        filename=filename,
        headers={"Content-Disposition": f'inline; filename="{filename}"'},
    )


@router.get("/presets", response_model=PresetsResponse)
async def get_presets():
    """Get available compression presets."""
    config = get_config()

    presets = [
        PresetItem(
            name=preset.name,
            label=preset.label,
            dpi=preset.dpi,
            quality=preset.quality,
            description=preset.description,
        )
        for preset in config.compression.presets
    ]

    return PresetsResponse(presets=presets)
