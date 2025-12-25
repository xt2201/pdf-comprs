"""
PDF Compression Service

Handles PDF compression using Ghostscript with configurable settings.
"""

import os
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from src.config import get_config
from src.logger import get_logger

logger = get_logger(__name__)


@dataclass
class CompressionResult:
    """Result of a compression operation."""

    success: bool
    initial_size_mb: float
    final_size_mb: float
    reduction_percent: float
    output_path: Optional[str] = None
    config_used: Optional[tuple[int, int, str]] = None
    target_reached: bool = False
    error: Optional[str] = None


class PDFCompressor:
    """PDF Compression service using Ghostscript."""

    def __init__(self):
        self.config = get_config()
        self.gs_config = self.config.ghostscript
        self.compression_config = self.config.compression

    def get_file_size_mb(self, filepath: str | Path) -> float:
        """Get file size in megabytes."""
        return os.path.getsize(filepath) / (1024 * 1024)

    def _build_gs_command(
        self,
        input_file: str,
        output_file: str,
        dpi: int,
        quality: int,
    ) -> list[str]:
        """Build Ghostscript command with parameters."""
        opts = self.gs_config.options

        cmd = [
            self.gs_config.executable,
            "-sDEVICE=pdfwrite",
            f"-dCompatibilityLevel={self.gs_config.compatibility_level}",
            f"-dPDFSETTINGS={self.gs_config.pdf_settings}",
            "-dNOPAUSE",
            "-dQUIET",
            "-dBATCH",
        ]

        # Downsampling options
        if opts.downsample_color_images:
            cmd.append("-dDownsampleColorImages=true")
            cmd.append(f"-dColorImageResolution={dpi}")
            cmd.append(f"-dColorImageDownsampleType={opts.downsample_type}")

        if opts.downsample_gray_images:
            cmd.append("-dDownsampleGrayImages=true")
            cmd.append(f"-dGrayImageResolution={dpi}")
            cmd.append(f"-dGrayImageDownsampleType={opts.downsample_type}")

        if opts.downsample_mono_images:
            cmd.append("-dDownsampleMonoImages=true")
            cmd.append(f"-dMonoImageResolution={dpi}")
            cmd.append(f"-dMonoImageDownsampleType={opts.downsample_type}")

        # Quality settings
        cmd.append(f"-dJPEGQ={quality}")

        # Other options
        if opts.detect_duplicate_images:
            cmd.append("-dDetectDuplicateImages=true")
        if opts.compress_fonts:
            cmd.append("-dCompressFonts=true")
        if opts.subset_fonts:
            cmd.append("-dSubsetFonts=true")
        if opts.embed_all_fonts:
            cmd.append("-dEmbedAllFonts=true")

        cmd.append(f"-dAutoRotatePages={opts.auto_rotate_pages}")
        cmd.append(f"-dColorConversionStrategy={opts.color_conversion_strategy}")

        if not opts.do_thumbnails:
            cmd.append("-dDoThumbnails=false")
        if not opts.create_job_ticket:
            cmd.append("-dCreateJobTicket=false")
        if not opts.preserve_eps_info:
            cmd.append("-dPreserveEPSInfo=false")
        if not opts.preserve_opi_comments:
            cmd.append("-dPreserveOPIComments=false")

        # Output file
        cmd.append(f"-sOutputFile={output_file}")
        cmd.append(input_file)

        return cmd

    def compress_with_settings(
        self,
        input_file: str,
        output_file: str,
        dpi: int,
        quality: int,
    ) -> tuple[bool, str]:
        """
        Compress PDF with specific settings.

        Args:
            input_file: Input PDF path
            output_file: Output PDF path
            dpi: Image resolution (lower = smaller file)
            quality: JPEG quality 0-100 (lower = smaller file)

        Returns:
            Tuple of (success, message)
        """
        cmd = self._build_gs_command(input_file, output_file, dpi, quality)

        logger.info(f"Compressing PDF: DPI={dpi}, Quality={quality}")
        logger.debug(f"Command: {' '.join(cmd)}")

        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            logger.info("Compression successful")
            return True, "Compression successful"
        except subprocess.CalledProcessError as e:
            error_msg = f"Compression error: {e.stderr}"
            logger.error(error_msg)
            return False, error_msg
        except FileNotFoundError:
            error_msg = (
                f"Ghostscript not found at '{self.gs_config.executable}'. "
                "Please install: sudo apt-get install ghostscript"
            )
            logger.error(error_msg)
            return False, error_msg

    def compress_to_target_size(
        self,
        input_file: str,
        output_file: str,
        target_size_mb: float,
    ) -> CompressionResult:
        """
        Progressively compress PDF to reach target size.

        Args:
            input_file: Input PDF path
            output_file: Output PDF path
            target_size_mb: Target file size in MB

        Returns:
            CompressionResult with compression details
        """
        if not os.path.exists(input_file):
            logger.error(f"Input file not found: {input_file}")
            return CompressionResult(
                success=False,
                initial_size_mb=0,
                final_size_mb=0,
                reduction_percent=0,
                error=f"Input file not found: {input_file}",
            )

        initial_size = self.get_file_size_mb(input_file)
        logger.info(f"Starting compression. Initial size: {initial_size:.2f} MB, Target: {target_size_mb} MB")

        # Get progressive configs from config
        configs = [
            (cfg.dpi, cfg.quality, cfg.description)
            for cfg in self.compression_config.progressive_configs
        ]

        if not configs:
            # Fallback to default configs
            configs = [
                (150, 80, "High quality"),
                (120, 70, "Good quality"),
                (96, 60, "Medium quality"),
                (72, 50, "Low quality"),
                (50, 40, "Very low quality"),
                (36, 30, "Minimal quality"),
                (30, 25, "Super compressed"),
                (24, 20, "Heavy compression"),
                (20, 15, "Maximum compression"),
                (15, 10, "Extreme compression"),
                (10, 5, "Ultra compression"),
            ]

        max_attempts = self.compression_config.max_attempts
        best_config = None

        for i, (dpi, quality, desc) in enumerate(configs[:max_attempts]):
            logger.info(f"Attempt {i + 1}: {desc} (DPI={dpi}, Quality={quality})")

            success, msg = self.compress_with_settings(input_file, output_file, dpi, quality)

            if not success:
                logger.warning(f"Compression attempt failed: {msg}")
                continue

            output_size = self.get_file_size_mb(output_file)
            logger.info(f"Result: {output_size:.2f} MB")

            if output_size <= target_size_mb:
                logger.info(f"Target reached with {desc}")
                return CompressionResult(
                    success=True,
                    initial_size_mb=initial_size,
                    final_size_mb=output_size,
                    reduction_percent=((initial_size - output_size) / initial_size) * 100,
                    output_path=output_file,
                    config_used=(dpi, quality, desc),
                    target_reached=True,
                )

            best_config = (dpi, quality, desc)

        # Check final result
        if os.path.exists(output_file):
            final_size = self.get_file_size_mb(output_file)
            reduction = ((initial_size - final_size) / initial_size) * 100 if initial_size > 0 else 0

            logger.info(
                f"Compression complete. Final size: {final_size:.2f} MB, "
                f"Reduction: {reduction:.1f}%"
            )

            return CompressionResult(
                success=True,
                initial_size_mb=initial_size,
                final_size_mb=final_size,
                reduction_percent=reduction,
                output_path=output_file,
                config_used=best_config,
                target_reached=final_size <= target_size_mb,
            )

        logger.error("Failed to compress PDF")
        return CompressionResult(
            success=False,
            initial_size_mb=initial_size,
            final_size_mb=0,
            reduction_percent=0,
            error="Failed to compress PDF",
        )


# Singleton instance
_compressor: Optional[PDFCompressor] = None


def get_pdf_compressor() -> PDFCompressor:
    """Get PDF compressor singleton instance."""
    global _compressor
    if _compressor is None:
        _compressor = PDFCompressor()
    return _compressor
