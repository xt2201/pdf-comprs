"""
Image to PDF Conversion Service

Handles converting images to PDF using PyMuPDF and Pillow.
"""

import os
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import fitz  # PyMuPDF
from PIL import Image

from src.logger import get_logger

logger = get_logger(__name__)


@dataclass
class ConversionResult:
    """Result of an image to PDF conversion."""

    success: bool
    page_count: int = 0
    output_path: Optional[str] = None
    size_mb: float = 0
    error: Optional[str] = None


class ImageConverter:
    """Image to PDF conversion service."""

    SUPPORTED_FORMATS = {".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".tif", ".webp"}

    def __init__(self):
        pass

    def is_supported_format(self, filepath: str | Path) -> bool:
        """Check if file format is supported."""
        ext = Path(filepath).suffix.lower()
        return ext in self.SUPPORTED_FORMATS

    def get_file_size_mb(self, filepath: str | Path) -> float:
        """Get file size in megabytes."""
        return os.path.getsize(filepath) / (1024 * 1024)

    def _convert_with_fitz(self, image_path: str, pdf_document: fitz.Document) -> bool:
        """Convert image to PDF using PyMuPDF (fitz)."""
        try:
            img_doc = fitz.open(image_path)
            pdf_bytes = img_doc.convert_to_pdf()
            img_pdf = fitz.open("pdf", pdf_bytes)
            pdf_document.insert_pdf(img_pdf)
            img_doc.close()
            img_pdf.close()
            return True
        except Exception as e:
            logger.warning(f"Fitz conversion failed for {image_path}: {e}")
            return False

    def _convert_with_pil(self, image_path: str, pdf_document: fitz.Document) -> bool:
        """Convert image to PDF using Pillow as fallback."""
        temp_pdf_path = None
        try:
            img = Image.open(image_path)

            # Convert to RGB if necessary
            if img.mode == "RGBA":
                # Create white background for transparent images
                background = Image.new("RGB", img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[3])
                img = background
            elif img.mode not in ["RGB", "L"]:
                img = img.convert("RGB")

            # Save to temporary PDF
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_pdf:
                temp_pdf_path = temp_pdf.name
                img.save(temp_pdf_path, "PDF", resolution=100.0)

            # Add to main document
            temp_doc = fitz.open(temp_pdf_path)
            pdf_document.insert_pdf(temp_doc)
            temp_doc.close()

            return True
        except Exception as e:
            logger.error(f"PIL conversion failed for {image_path}: {e}")
            return False
        finally:
            if temp_pdf_path and os.path.exists(temp_pdf_path):
                os.unlink(temp_pdf_path)

    def convert_images_to_pdf(
        self,
        image_paths: list[str],
        output_pdf: str,
    ) -> ConversionResult:
        """
        Convert a list of images to a single PDF.

        Args:
            image_paths: List of image file paths in desired order
            output_pdf: Output PDF path

        Returns:
            ConversionResult with conversion details
        """
        if not image_paths:
            logger.warning("No images provided for conversion")
            return ConversionResult(
                success=False,
                error="No images provided",
            )

        # Filter valid images
        valid_images = []
        for path in image_paths:
            if path and os.path.exists(path):
                if self.is_supported_format(path):
                    valid_images.append(path)
                else:
                    logger.warning(f"Unsupported format: {path}")
            else:
                logger.warning(f"Image not found: {path}")

        if not valid_images:
            logger.error("No valid image files found")
            return ConversionResult(
                success=False,
                error="No valid image files found",
            )

        logger.info(f"Converting {len(valid_images)} images to PDF")

        try:
            pdf_document = fitz.open()

            for i, img_path in enumerate(valid_images):
                logger.debug(f"Processing image {i + 1}/{len(valid_images)}: {img_path}")

                # Try fitz first, then PIL as fallback
                if not self._convert_with_fitz(img_path, pdf_document):
                    if not self._convert_with_pil(img_path, pdf_document):
                        # Close document and return error
                        pdf_document.close()
                        return ConversionResult(
                            success=False,
                            error=f"Failed to process image: {os.path.basename(img_path)}",
                        )

            # Ensure output directory exists
            output_path = Path(output_pdf)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Save the final PDF
            pdf_document.save(output_pdf)
            pdf_document.close()

            size_mb = self.get_file_size_mb(output_pdf)
            logger.info(f"PDF created successfully: {len(valid_images)} pages, {size_mb:.2f} MB")

            return ConversionResult(
                success=True,
                page_count=len(valid_images),
                output_path=output_pdf,
                size_mb=size_mb,
            )

        except Exception as e:
            logger.error(f"Error creating PDF: {e}")
            return ConversionResult(
                success=False,
                error=f"Error creating PDF: {str(e)}",
            )

    def get_images_info(self, image_paths: list[str]) -> dict:
        """Get summary information about images."""
        valid_images = [
            p for p in image_paths
            if p and os.path.exists(p) and self.is_supported_format(p)
        ]

        if not valid_images:
            return {
                "count": 0,
                "total_size_mb": 0,
                "files": [],
            }

        total_size = sum(os.path.getsize(p) for p in valid_images) / (1024 * 1024)

        return {
            "count": len(valid_images),
            "total_size_mb": round(total_size, 2),
            "files": [
                {
                    "name": os.path.basename(p),
                    "size_mb": round(os.path.getsize(p) / (1024 * 1024), 2),
                }
                for p in valid_images
            ],
        }


# Singleton instance
_converter: Optional[ImageConverter] = None


def get_image_converter() -> ImageConverter:
    """Get image converter singleton instance."""
    global _converter
    if _converter is None:
        _converter = ImageConverter()
    return _converter
