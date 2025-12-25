# Project Folder Structure

```
pdf-comprs/
├── docs/                           # Documentation
│   ├── PLAN.md                     # Implementation plan & progress
│   ├── FOLDER_STRUCTURE.md         # This file
│   └── API.md                      # API documentation
│
├── backend/                        # Python FastAPI backend
│   ├── src/
│   │   ├── __init__.py
│   │   ├── main.py                 # FastAPI application entry
│   │   ├── config.py               # Configuration loader
│   │   ├── logger.py               # Unified logging system
│   │   │
│   │   ├── api/                    # API routes
│   │   │   ├── __init__.py
│   │   │   ├── routes.py           # Main router
│   │   │   ├── compression.py      # Compression endpoints
│   │   │   └── health.py           # Health check endpoint
│   │   │
│   │   ├── services/               # Business logic
│   │   │   ├── __init__.py
│   │   │   ├── pdf_compressor.py   # PDF compression service
│   │   │   ├── image_converter.py  # Image to PDF conversion
│   │   │   └── file_manager.py     # File handling utilities
│   │   │
│   │   ├── models/                 # Pydantic models
│   │   │   ├── __init__.py
│   │   │   ├── requests.py         # Request models
│   │   │   └── responses.py        # Response models
│   │   │
│   │   └── utils/                  # Utilities
│   │       ├── __init__.py
│   │       └── ngrok_tunnel.py     # Ngrok integration
│   │
│   ├── tests/                      # Backend tests
│   │   └── __init__.py
│   │
│   └── pyproject.toml              # Python dependencies (uv)
│
├── frontend/                       # React frontend
│   ├── src/
│   │   ├── main.tsx                # React entry point
│   │   ├── App.tsx                 # Main App component
│   │   ├── index.css               # Global styles
│   │   │
│   │   ├── components/             # React components
│   │   │   ├── ui/                 # shadcn/ui components
│   │   │   │   ├── button.tsx
│   │   │   │   ├── card.tsx
│   │   │   │   ├── slider.tsx
│   │   │   │   ├── tabs.tsx
│   │   │   │   ├── switch.tsx
│   │   │   │   ├── progress.tsx
│   │   │   │   └── ...
│   │   │   │
│   │   │   ├── layout/             # Layout components
│   │   │   │   ├── Header.tsx
│   │   │   │   ├── Footer.tsx
│   │   │   │   ├── Sidebar.tsx
│   │   │   │   └── MainLayout.tsx
│   │   │   │
│   │   │   ├── compression/        # Compression feature
│   │   │   │   ├── CompressionPanel.tsx
│   │   │   │   ├── SettingsForm.tsx
│   │   │   │   ├── PresetButtons.tsx
│   │   │   │   └── ResultDisplay.tsx
│   │   │   │
│   │   │   ├── upload/             # Upload feature
│   │   │   │   ├── UploadZone.tsx
│   │   │   │   ├── FileList.tsx
│   │   │   │   ├── ImageItem.tsx
│   │   │   │   └── PDFUploader.tsx
│   │   │   │
│   │   │   ├── preview/            # Preview feature
│   │   │   │   ├── ImagePreview.tsx
│   │   │   │   └── PDFPreview.tsx
│   │   │   │
│   │   │   └── three/              # Three.js components
│   │   │       ├── Background3D.tsx
│   │   │       ├── FloatingShapes.tsx
│   │   │       └── ParticleField.tsx
│   │   │
│   │   ├── hooks/                  # Custom React hooks
│   │   │   ├── useCompression.ts
│   │   │   ├── useFileUpload.ts
│   │   │   └── useTheme.ts
│   │   │
│   │   ├── stores/                 # Zustand stores
│   │   │   ├── compressionStore.ts
│   │   │   ├── fileStore.ts
│   │   │   └── themeStore.ts
│   │   │
│   │   ├── services/               # API services
│   │   │   ├── api.ts              # Axios instance
│   │   │   └── compressionApi.ts   # Compression API calls
│   │   │
│   │   ├── types/                  # TypeScript types
│   │   │   └── index.ts
│   │   │
│   │   └── lib/                    # Utility functions
│   │       ├── utils.ts            # General utilities
│   │       └── cn.ts               # Class name helper
│   │
│   ├── public/                     # Static assets
│   │   └── favicon.ico
│   │
│   ├── package.json                # Node dependencies
│   ├── tsconfig.json               # TypeScript config
│   ├── vite.config.ts              # Vite config
│   ├── tailwind.config.ts          # Tailwind config
│   ├── postcss.config.js           # PostCSS config
│   └── components.json             # shadcn/ui config
│
├── config.yml                      # Main configuration file
├── run.py                          # Main entry script
├── README.md                       # Project README
└── .gitignore                      # Git ignore rules
```

## Key Files Description

### Configuration
- `config.yml` - Central configuration for all settings (no hardcoding)

### Backend
- `main.py` - FastAPI app initialization and middleware
- `logger.py` - Unified logging system used throughout
- `pdf_compressor.py` - Ghostscript-based compression logic
- `image_converter.py` - PyMuPDF/PIL image to PDF conversion

### Frontend
- `Background3D.tsx` - Three.js animated background
- `CompressionPanel.tsx` - Main compression interface
- `UploadZone.tsx` - Drag & drop file upload

### Entry Point
- `run.py` - Single script to start both frontend and backend
