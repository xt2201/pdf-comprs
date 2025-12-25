import { create } from 'zustand'
import type { CompressionResult, ImageToPdfResult, CompressionPreset } from '@/types'

interface CompressionState {
  // State
  isProcessing: boolean
  progress: number
  result: CompressionResult | ImageToPdfResult | null
  error: string | null
  presets: CompressionPreset[]
  
  // Actions
  setProcessing: (isProcessing: boolean) => void
  setProgress: (progress: number) => void
  setResult: (result: CompressionResult | ImageToPdfResult | null) => void
  setError: (error: string | null) => void
  setPresets: (presets: CompressionPreset[]) => void
  reset: () => void
}

export const useCompressionStore = create<CompressionState>((set) => ({
  isProcessing: false,
  progress: 0,
  result: null,
  error: null,
  presets: [],

  setProcessing: (isProcessing: boolean) => {
    set({ isProcessing })
    if (isProcessing) {
      set({ error: null })
    }
  },

  setProgress: (progress: number) => {
    set({ progress })
  },

  setResult: (result: CompressionResult | ImageToPdfResult | null) => {
    // Validate result has required properties
    if (result) {
      const hasRequiredProps = 
        typeof result.success === 'boolean' &&
        typeof result.jobId === 'string' &&
        typeof result.originalSizeMb === 'number' &&
        typeof result.compressedSizeMb === 'number' &&
        typeof result.reductionPercent === 'number'
      
      if (!hasRequiredProps) {
        console.error('Invalid result object received:', result)
        set({ 
          error: 'Invalid response from server', 
          isProcessing: false, 
          result: null 
        })
        return
      }
    }
    set({ result, isProcessing: false, progress: 100 })
  },

  setError: (error: string | null) => {
    set({ error, isProcessing: false })
  },

  setPresets: (presets: CompressionPreset[]) => {
    set({ presets })
  },

  reset: () => {
    set({
      isProcessing: false,
      progress: 0,
      result: null,
      error: null,
    })
  },
}))
