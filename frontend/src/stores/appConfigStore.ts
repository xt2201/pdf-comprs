import { create } from 'zustand'

interface AppConfig {
  name: string
  title: string
  version: string
  description: string
  logoUrl: string
}

interface AppConfigState {
  config: AppConfig | null
  isLoading: boolean
  error: string | null
  fetchConfig: () => Promise<void>
}

const defaultConfig: AppConfig = {
  name: 'PDF Compression Tool',
  title: 'PDF Compression Tool',
  version: '1.0.0',
  description: 'PDF compression with image to PDF conversion',
  logoUrl: '',
}

export const useAppConfigStore = create<AppConfigState>((set) => ({
  config: defaultConfig,
  isLoading: false,
  error: null,

  fetchConfig: async () => {
    set({ isLoading: true, error: null })
    try {
      const response = await fetch('/api/app-info')
      if (!response.ok) {
        throw new Error('Failed to fetch app config')
      }
      const data = await response.json()
      set({
        config: {
          name: data.name,
          title: data.title,
          version: data.version,
          description: data.description,
          logoUrl: data.logo_url,
        },
        isLoading: false,
      })
    } catch (error) {
      console.error('Failed to load app config:', error)
      set({ error: 'Failed to load app config', isLoading: false })
      // Keep using default config on error
    }
  },
}))
