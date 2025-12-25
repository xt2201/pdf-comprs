// ============================================================================
// Type Definitions
// ============================================================================

export interface CompressionSettings {
  targetSizeMb: number
  dpi: number
  quality: number
  autoCompress: boolean
  outputFilename: string
}

export interface CompressionPreset {
  name: string
  label: string
  dpi: number
  quality: number
  description: string
}

export interface CompressionResult {
  success: boolean
  jobId: string
  originalSizeMb: number
  compressedSizeMb: number
  reductionPercent: number
  configUsed?: {
    dpi: number
    quality: number
    description: string
  }
  targetReached: boolean
  downloadUrl: string
  message: string
}

export interface ImageToPdfResult {
  success: boolean
  jobId: string
  pages: number
  originalSizeMb: number
  compressedSizeMb: number
  reductionPercent: number
  downloadUrl: string
  message: string
}

export interface JobStatus {
  jobId: string
  status: 'pending' | 'processing' | 'completed' | 'failed'
  progress: number
  message: string
}

export interface UploadedFile {
  id: string
  file: File
  preview?: string
  order: number
}

export interface ApiError {
  code: string
  message: string
}

export type ThemeMode = 'light' | 'dark' | 'system'
