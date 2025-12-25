import { create } from 'zustand'
import type { UploadedFile, CompressionSettings } from '@/types'

interface FileState {
  // Image files for conversion
  imageFiles: UploadedFile[]
  // PDF file for compression
  pdfFile: File | null
  
  // Settings
  settings: CompressionSettings
  
  // Actions
  addImageFiles: (files: File[]) => void
  removeImageFile: (id: string) => void
  reorderImageFiles: (activeId: string, overId: string) => void
  clearImageFiles: () => void
  
  setPdfFile: (file: File | null) => void
  clearPdfFile: () => void
  
  updateSettings: (settings: Partial<CompressionSettings>) => void
  resetSettings: () => void
}

const defaultSettings: CompressionSettings = {
  targetSizeMb: 0.5,
  dpi: 72,
  quality: 50,
  autoCompress: true,
  outputFilename: 'output',
}

let fileIdCounter = 0

export const useFileStore = create<FileState>((set, get) => ({
  imageFiles: [],
  pdfFile: null,
  settings: { ...defaultSettings },

  addImageFiles: (files: File[]) => {
    const { imageFiles } = get()
    const newFiles: UploadedFile[] = files.map((file, index) => {
      const id = `file-${fileIdCounter++}`
      return {
        id,
        file,
        preview: file.type.startsWith('image/') ? URL.createObjectURL(file) : undefined,
        order: imageFiles.length + index,
      }
    })
    set({ imageFiles: [...imageFiles, ...newFiles] })
  },

  removeImageFile: (id: string) => {
    const { imageFiles } = get()
    const fileToRemove = imageFiles.find((f) => f.id === id)
    if (fileToRemove?.preview) {
      URL.revokeObjectURL(fileToRemove.preview)
    }
    const remaining = imageFiles.filter((f) => f.id !== id)
    // Re-order remaining files
    const reordered = remaining.map((f, index) => ({ ...f, order: index }))
    set({ imageFiles: reordered })
  },

  reorderImageFiles: (activeId: string, overId: string) => {
    const { imageFiles } = get()
    const activeIndex = imageFiles.findIndex((f) => f.id === activeId)
    const overIndex = imageFiles.findIndex((f) => f.id === overId)
    
    if (activeIndex === -1 || overIndex === -1) return
    
    const newFiles = [...imageFiles]
    const [movedItem] = newFiles.splice(activeIndex, 1)
    newFiles.splice(overIndex, 0, movedItem)
    
    // Update order property
    const reordered = newFiles.map((f, index) => ({ ...f, order: index }))
    set({ imageFiles: reordered })
  },

  clearImageFiles: () => {
    const { imageFiles } = get()
    imageFiles.forEach((f) => {
      if (f.preview) {
        URL.revokeObjectURL(f.preview)
      }
    })
    set({ imageFiles: [] })
  },

  setPdfFile: (file: File | null) => {
    set({ pdfFile: file })
  },

  clearPdfFile: () => {
    set({ pdfFile: null })
  },

  updateSettings: (newSettings: Partial<CompressionSettings>) => {
    const { settings } = get()
    set({ settings: { ...settings, ...newSettings } })
  },

  resetSettings: () => {
    set({ settings: { ...defaultSettings } })
  },
}))
