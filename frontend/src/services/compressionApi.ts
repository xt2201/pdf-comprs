import api from './api'
import type {
  CompressionResult,
  ImageToPdfResult,
  JobStatus,
  CompressionPreset,
  CompressionSettings,
} from '@/types'

// ============================================================================
// Compression API Service
// ============================================================================

export async function compressPdf(
  file: File,
  settings: CompressionSettings,
  onProgress?: (progress: number) => void
): Promise<CompressionResult> {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('target_size_mb', settings.targetSizeMb.toString())
  formData.append('dpi', settings.dpi.toString())
  formData.append('quality', settings.quality.toString())
  formData.append('auto_compress', settings.autoCompress.toString())
  formData.append('output_filename', settings.outputFilename)

  const response = await api.post<CompressionResult>('/compress/pdf', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
    onUploadProgress: (progressEvent) => {
      if (progressEvent.total && onProgress) {
        const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total)
        onProgress(progress)
      }
    },
  })

  return {
    success: response.data.success,
    jobId: (response.data as any).job_id || response.data.jobId,
    originalSizeMb: (response.data as any).original_size_mb ?? response.data.originalSizeMb,
    compressedSizeMb: (response.data as any).compressed_size_mb ?? response.data.compressedSizeMb,
    reductionPercent: (response.data as any).reduction_percent ?? response.data.reductionPercent,
    configUsed: (response.data as any).config_used || response.data.configUsed,
    targetReached: (response.data as any).target_reached ?? response.data.targetReached,
    downloadUrl: (response.data as any).download_url || response.data.downloadUrl,
    message: response.data.message,
  }
}

export async function imagesToPdf(
  files: File[],
  settings: CompressionSettings,
  onProgress?: (progress: number) => void
): Promise<ImageToPdfResult> {
  const formData = new FormData()
  
  // Append files in order
  files.forEach((file) => {
    formData.append('files', file)
  })
  
  formData.append('target_size_mb', settings.targetSizeMb.toString())
  formData.append('dpi', settings.dpi.toString())
  formData.append('quality', settings.quality.toString())
  formData.append('auto_compress', settings.autoCompress.toString())
  formData.append('output_filename', settings.outputFilename)

  const response = await api.post<ImageToPdfResult>('/compress/images-to-pdf', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
    onUploadProgress: (progressEvent) => {
      if (progressEvent.total && onProgress) {
        const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total)
        onProgress(progress)
      }
    },
  })

  return {
    success: response.data.success,
    jobId: (response.data as any).job_id || response.data.jobId,
    pages: response.data.pages,
    originalSizeMb: (response.data as any).original_size_mb ?? response.data.originalSizeMb,
    compressedSizeMb: (response.data as any).compressed_size_mb ?? response.data.compressedSizeMb,
    reductionPercent: (response.data as any).reduction_percent ?? response.data.reductionPercent,
    downloadUrl: (response.data as any).download_url || response.data.downloadUrl,
    message: response.data.message,
  }
}

export async function getJobStatus(jobId: string): Promise<JobStatus> {
  const response = await api.get<JobStatus>(`/compress/status/${jobId}`)
  return response.data
}

export async function getPresets(): Promise<CompressionPreset[]> {
  const response = await api.get<{ presets: CompressionPreset[] }>('/compress/presets')
  return response.data.presets
}

export function getDownloadUrl(jobId: string): string {
  return `/api/compress/download/${jobId}`
}

export async function downloadFile(jobId: string, filename: string): Promise<void> {
  const response = await api.get(`/compress/download/${jobId}`, {
    responseType: 'blob',
    headers: {
      'Accept': 'application/pdf',
    },
  })

  // Ensure filename has .pdf extension
  const pdfFilename = filename.endsWith('.pdf') ? filename : `${filename}.pdf`

  // Create download link
  const blob = new Blob([response.data], { type: 'application/pdf' })
  const url = window.URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.setAttribute('download', pdfFilename)
  document.body.appendChild(link)
  link.click()
  link.remove()
  window.URL.revokeObjectURL(url)
}

export async function checkHealth(): Promise<boolean> {
  try {
    await api.get('/health')
    return true
  } catch {
    return false
  }
}
