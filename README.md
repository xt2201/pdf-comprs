# PDF Compression Tool

PDF compression web application with image to PDF conversion.

## Features

- Convert multiple images to PDF with drag-and-drop reordering
- Compress existing PDFs with customizable settings
- Auto-compression to reach target file size
- Modern UI with Three.js 3D background effects
- Light/Dark theme support
- Local deployment with optional ngrok public access

## Requirements

- Python 3.11+
- Node.js 18+
- Ghostscript

### Install Dependencies

**Linux (Ubuntu/Debian):**
```bash
# Ghostscript
sudo apt-get install ghostscript

# uv (Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Node.js (using nvm)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
nvm install 18
```

**macOS:**
```bash
# Ghostscript
brew install ghostscript

# uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Node.js
brew install node
```

## Quick Start

### 1. Setup

```bash
# Check requirements
python run.py --check

# Install all dependencies
python run.py --setup
```

### 2. Run Application

**Option A: Run backend and frontend separately (recommended for development)**

Terminal 1:
```bash
python run.py --backend-only
```

Terminal 2:
```bash
python run.py --frontend-only
```

**Option B: Run backend only**

```bash
python run.py --backend-only
```

Then open `http://localhost:8007/api/docs` for API documentation.

### 3. Access

- Frontend: http://localhost:3007
- Backend API: http://localhost:8007
- API Docs: http://localhost:8007/api/docs

## Configuration

All settings are in `config.yml`. Key configurations:

```yaml
# Server ports
server:
  backend:
    port: 8007
  frontend:
    port: 3007

# Enable public access via ngrok
ngrok:
  enabled: false  # Set to true for public URL
  auth_token: ""  # Optional ngrok auth token

# Compression defaults
compression:
  default:
    target_size_mb: 0.5
    dpi: 72
    quality: 50
```

## Project Structure

```
pdf-comprs/
├── backend/          # FastAPI Python backend
│   ├── src/
│   │   ├── api/      # API endpoints
│   │   ├── services/ # Business logic
│   │   └── models/   # Pydantic models
│   └── pyproject.toml
├── frontend/         # React TypeScript frontend
│   ├── src/
│   │   ├── components/
│   │   ├── stores/
│   │   └── services/
│   └── package.json
├── docs/             # Documentation
├── config.yml        # Main configuration
└── run.py            # Entry point script
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check |
| POST | `/api/compress/pdf` | Compress PDF file |
| POST | `/api/compress/images-to-pdf` | Convert images to PDF |
| GET | `/api/compress/status/{job_id}` | Check job status |
| GET | `/api/compress/download/{job_id}` | Download result |
| GET | `/api/compress/presets` | Get compression presets |

## Development

### Backend

```bash
cd backend
uv sync
uv run uvicorn src.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## License

MIT
