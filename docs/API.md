# API Documentation

## Base URL
- **Local**: `http://localhost:8007`
- **Public (ngrok)**: Dynamic URL from ngrok

## Authentication
No authentication required for local deployment.

---

## Endpoints

### Health Check

#### GET /api/health
Check if the API is running.

**Response**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2024-12-23T10:00:00Z"
}
```

---

### PDF Compression

#### POST /api/compress/pdf
Compress an existing PDF file.

**Request**
- `Content-Type`: `multipart/form-data`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| file | File | Yes | PDF file to compress |
| target_size_mb | float | No | Target size in MB (default: 0.5) |
| dpi | int | No | Image resolution (default: 72) |
| quality | int | No | JPEG quality 0-100 (default: 50) |
| auto_compress | bool | No | Auto-find best settings (default: true) |
| output_filename | string | No | Output filename (default: "compressed") |

**Response**
```json
{
  "success": true,
  "job_id": "uuid-string",
  "original_size_mb": 5.2,
  "compressed_size_mb": 0.45,
  "reduction_percent": 91.3,
  "config_used": {
    "dpi": 72,
    "quality": 50,
    "description": "Low quality"
  },
  "target_reached": true,
  "download_url": "/api/compress/download/uuid-string"
}
```

---

#### POST /api/compress/images-to-pdf
Convert images to PDF and optionally compress.

**Request**
- `Content-Type`: `multipart/form-data`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| files | File[] | Yes | Image files (in order) |
| target_size_mb | float | No | Target size in MB (default: 0.5) |
| dpi | int | No | Image resolution (default: 72) |
| quality | int | No | JPEG quality 0-100 (default: 50) |
| auto_compress | bool | No | Auto-compress after creation (default: true) |
| output_filename | string | No | Output filename (default: "output") |

**Response**
```json
{
  "success": true,
  "job_id": "uuid-string",
  "pages": 5,
  "original_size_mb": 2.1,
  "compressed_size_mb": 0.48,
  "reduction_percent": 77.1,
  "download_url": "/api/compress/download/uuid-string"
}
```

---

#### GET /api/compress/status/{job_id}
Check compression job status.

**Response**
```json
{
  "job_id": "uuid-string",
  "status": "completed",
  "progress": 100,
  "message": "Compression successful"
}
```

Status values: `pending`, `processing`, `completed`, `failed`

---

#### GET /api/compress/download/{job_id}
Download the compressed PDF file.

**Response**
- `Content-Type`: `application/pdf`
- `Content-Disposition`: `attachment; filename="compressed.pdf"`

---

### Settings

#### GET /api/settings/presets
Get available compression presets.

**Response**
```json
{
  "presets": [
    {
      "name": "high_quality",
      "label": "High Quality",
      "dpi": 150,
      "quality": 80
    },
    {
      "name": "medium",
      "label": "Medium",
      "dpi": 96,
      "quality": 60
    },
    {
      "name": "low_size",
      "label": "Low Size",
      "dpi": 50,
      "quality": 30
    }
  ]
}
```

---

## Error Responses

All error responses follow this format:

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable error message"
  }
}
```

### Error Codes
| Code | HTTP Status | Description |
|------|-------------|-------------|
| FILE_NOT_FOUND | 404 | Requested file not found |
| INVALID_FILE_TYPE | 400 | File type not supported |
| COMPRESSION_FAILED | 500 | Compression process failed |
| GHOSTSCRIPT_NOT_FOUND | 500 | Ghostscript not installed |
| FILE_TOO_LARGE | 413 | File exceeds maximum size |

---

## Rate Limits
No rate limits for local deployment.

## File Size Limits
- Maximum upload size: Configurable in `config.yml`
- Default: 100 MB
