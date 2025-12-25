#!/usr/bin/env python3
"""
PDF Compression Tool - Main Entry Point

This script starts both the backend API server and optionally the frontend.
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path

# Project root directory
PROJECT_ROOT = Path(__file__).parent.absolute()
BACKEND_DIR = PROJECT_ROOT / "backend"
FRONTEND_DIR = PROJECT_ROOT / "frontend"
CONFIG_FILE = PROJECT_ROOT / "config.yml"


def load_config():
    """Load configuration from config.yml."""
    try:
        import yaml

        with open(CONFIG_FILE, "r") as f:
            return yaml.safe_load(f)
    except ImportError:
        print("PyYAML not installed. Install with: pip install pyyaml")
        sys.exit(1)
    except FileNotFoundError:
        print(f"Config file not found: {CONFIG_FILE}")
        sys.exit(1)


def check_ghostscript():
    """Check if Ghostscript is installed."""
    try:
        result = subprocess.run(
            ["gs", "--version"],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            print(f"✓ Ghostscript version: {result.stdout.strip()}")
            return True
    except FileNotFoundError:
        pass

    print("✗ Ghostscript not found!")
    print("  Install with: sudo apt-get install ghostscript (Linux)")
    print("             or: brew install ghostscript (macOS)")
    return False


def setup_backend():
    """Set up and run the backend server."""
    os.chdir(BACKEND_DIR)

    # Check if uv is available
    try:
        subprocess.run(["uv", "--version"], capture_output=True, check=True)
        print("✓ Using uv for Python environment")
    except (FileNotFoundError, subprocess.CalledProcessError):
        print("✗ uv not found. Install with: curl -LsSf https://astral.sh/uv/install.sh | sh")
        sys.exit(1)

    # Sync dependencies
    print("\n📦 Installing backend dependencies...")
    subprocess.run(["uv", "sync"], check=True)

    return True


def run_backend(config):
    """Run the backend server."""
    os.chdir(BACKEND_DIR)

    server_config = config.get("server", {}).get("backend", {})
    host = server_config.get("host", "0.0.0.0")
    port = server_config.get("port", 8007)
    reload = server_config.get("reload", True)

    print(f"\n🚀 Starting backend server at http://{host}:{port}")

    cmd = [
        "uv", "run", "uvicorn", "src.main:app",
        "--host", host,
        "--port", str(port),
    ]

    if reload:
        cmd.append("--reload")

    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n\n👋 Backend server stopped")


def setup_frontend():
    """Set up the frontend."""
    os.chdir(FRONTEND_DIR)

    # Check if node/npm is available
    try:
        subprocess.run(["node", "--version"], capture_output=True, check=True)
        print("✓ Node.js found")
    except (FileNotFoundError, subprocess.CalledProcessError):
        print("✗ Node.js not found. Please install Node.js 18+")
        return False

    # Install dependencies
    print("\n📦 Installing frontend dependencies...")
    subprocess.run(["npm", "install"], check=True)

    return True


def run_frontend(config):
    """Run the frontend development server."""
    os.chdir(FRONTEND_DIR)

    server_config = config.get("server", {}).get("frontend", {})
    port = server_config.get("port", 3000)

    print(f"\n🎨 Starting frontend at http://localhost:{port}")

    try:
        subprocess.run(["npm", "run", "dev"])
    except KeyboardInterrupt:
        print("\n\n👋 Frontend server stopped")


def main():
    parser = argparse.ArgumentParser(
        description="PDF Compression Tool - Run the application"
    )
    parser.add_argument(
        "--backend-only",
        action="store_true",
        help="Run only the backend server",
    )
    parser.add_argument(
        "--frontend-only",
        action="store_true",
        help="Run only the frontend server",
    )
    parser.add_argument(
        "--setup",
        action="store_true",
        help="Only set up dependencies, don't run servers",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check system requirements",
    )

    args = parser.parse_args()

    print("=" * 60)
    print("  PDF Compression Tool")
    print("=" * 60)

    # Load configuration
    config = load_config()
    print(f"✓ Configuration loaded from {CONFIG_FILE}")

    # Check requirements
    if args.check or not (args.frontend_only):
        if not check_ghostscript():
            if not args.check:
                print("\n⚠️  Ghostscript is required for PDF compression")

    if args.check:
        print("\n✓ System check complete")
        return

    # Setup mode
    if args.setup:
        if not args.frontend_only:
            setup_backend()
        if not args.backend_only:
            setup_frontend()
        print("\n✓ Setup complete")
        return

    # Run servers
    if args.frontend_only:
        if setup_frontend():
            run_frontend(config)
    elif args.backend_only:
        if setup_backend():
            run_backend(config)
    else:
        # Run both (backend in foreground)
        print("\n💡 Tip: Run frontend in a separate terminal with: python run.py --frontend-only")
        if setup_backend():
            run_backend(config)


if __name__ == "__main__":
    main()
