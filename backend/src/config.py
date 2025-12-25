"""
Configuration Management

Loads and validates configuration from config.yml.
Provides typed access to all configuration values.
"""

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


class ServerBackendConfig(BaseModel):
    """Backend server configuration."""

    host: str = "0.0.0.0"
    port: int = 8007
    reload: bool = True
    workers: int = 1


class ServerFrontendConfig(BaseModel):
    """Frontend server configuration."""

    host: str = "localhost"
    port: int = 3007


class CorsConfig(BaseModel):
    """CORS configuration."""

    allow_origins: list[str] = ["http://localhost:3007"]
    allow_methods: list[str] = ["GET", "POST", "DELETE"]
    allow_headers: list[str] = ["*"]


class ServerConfig(BaseModel):
    """Server configuration."""

    backend: ServerBackendConfig = ServerBackendConfig()
    frontend: ServerFrontendConfig = ServerFrontendConfig()
    cors: CorsConfig = CorsConfig()


class NgrokConfig(BaseModel):
    """Ngrok tunnel configuration."""

    enabled: bool = False
    auth_token: str = ""
    region: str = "us"
    domain: str = ""


class UploadConfig(BaseModel):
    """File upload configuration."""

    max_file_size_mb: int = 100
    allowed_image_types: list[str] = [".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".webp"]
    allowed_pdf_types: list[str] = [".pdf"]
    temp_directory: str = ""


class CompressionPreset(BaseModel):
    """Single compression preset."""

    name: str
    label: str
    dpi: int
    quality: int
    description: str = ""


class ProgressiveConfig(BaseModel):
    """Progressive compression configuration."""

    dpi: int
    quality: int
    description: str


class CompressionDefaultConfig(BaseModel):
    """Default compression settings."""

    target_size_mb: float = 0.5
    dpi: int = 72
    quality: int = 50
    auto_compress: bool = True


class CompressionConfig(BaseModel):
    """Compression configuration."""

    default: CompressionDefaultConfig = CompressionDefaultConfig()
    presets: list[CompressionPreset] = []
    progressive_configs: list[ProgressiveConfig] = []
    max_attempts: int = 11


class GhostscriptOptionsConfig(BaseModel):
    """Ghostscript options."""

    downsample_color_images: bool = True
    downsample_gray_images: bool = True
    downsample_mono_images: bool = True
    downsample_type: str = "/Bicubic"
    detect_duplicate_images: bool = True
    compress_fonts: bool = True
    subset_fonts: bool = True
    embed_all_fonts: bool = True
    auto_rotate_pages: str = "/None"
    color_conversion_strategy: str = "/LeaveColorUnchanged"
    do_thumbnails: bool = False
    create_job_ticket: bool = False
    preserve_eps_info: bool = False
    preserve_opi_comments: bool = False


class GhostscriptConfig(BaseModel):
    """Ghostscript configuration."""

    executable: str = "gs"
    pdf_settings: str = "/screen"
    compatibility_level: str = "1.4"
    options: GhostscriptOptionsConfig = GhostscriptOptionsConfig()


class LoggingFileConfig(BaseModel):
    """File logging configuration."""

    enabled: bool = True
    path: str = "logs/app.log"
    max_size_mb: int = 10
    backup_count: int = 5


class LoggingConsoleConfig(BaseModel):
    """Console logging configuration."""

    enabled: bool = True
    colorized: bool = True


class LoggingConfig(BaseModel):
    """Logging configuration."""

    level: str = "INFO"
    format: str = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    date_format: str = "%Y-%m-%d %H:%M:%S"
    file: LoggingFileConfig = LoggingFileConfig()
    console: LoggingConsoleConfig = LoggingConsoleConfig()


class ThreeJsBackgroundConfig(BaseModel):
    """Three.js background configuration."""

    particle_count: int = 100
    animation_speed: float = 0.5
    color_primary: str = "#667eea"
    color_secondary: str = "#764ba2"


class ThreeJsConfig(BaseModel):
    """Three.js configuration."""

    enabled: bool = True
    background: ThreeJsBackgroundConfig = ThreeJsBackgroundConfig()


class ThemeConfig(BaseModel):
    """Theme configuration."""

    default_mode: str = "system"


class UIConfig(BaseModel):
    """UI configuration."""

    title: str = "PDF Compression Tool"
    logo_url: str = ""
    theme: ThemeConfig = ThemeConfig()
    three_js: ThreeJsConfig = ThreeJsConfig()


class CleanupConfig(BaseModel):
    """Cleanup configuration."""

    enabled: bool = True
    max_age_hours: int = 24
    interval_minutes: int = 60


class AppInfoConfig(BaseModel):
    """Application info configuration."""

    name: str = "Bủm Xiu PDF Compression Tool"
    version: str = "1.0.0"
    description: str = "Bủm Xiu PDF compression with image to PDF conversion"


class AppConfig(BaseModel):
    """Complete application configuration."""

    app: AppInfoConfig = AppInfoConfig()
    server: ServerConfig = ServerConfig()
    ngrok: NgrokConfig = NgrokConfig()
    upload: UploadConfig = UploadConfig()
    compression: CompressionConfig = CompressionConfig()
    ghostscript: GhostscriptConfig = GhostscriptConfig()
    logging: LoggingConfig = LoggingConfig()
    ui: UIConfig = UIConfig()
    cleanup: CleanupConfig = CleanupConfig()


def load_yaml_config(config_path: str | Path) -> dict[str, Any]:
    """Load configuration from YAML file."""
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


@lru_cache
def get_config(config_path: str | None = None) -> AppConfig:
    """
    Get application configuration.

    Args:
        config_path: Path to config.yml file. If None, uses default path.

    Returns:
        Validated AppConfig instance
    """
    if config_path is None:
        # Look for config.yml in project root
        root_path = Path(__file__).parent.parent.parent / "config.yml"
        config_path = str(root_path)

    yaml_data = load_yaml_config(config_path)
    return AppConfig(**yaml_data)


def get_config_dict(config_path: str | None = None) -> dict[str, Any]:
    """
    Get configuration as dictionary for logging setup.

    Args:
        config_path: Path to config.yml file

    Returns:
        Configuration as dictionary
    """
    if config_path is None:
        root_path = Path(__file__).parent.parent.parent / "config.yml"
        config_path = str(root_path)

    return load_yaml_config(config_path)
