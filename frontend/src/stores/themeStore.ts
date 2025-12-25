import { create } from 'zustand'
import type { ThemeMode } from '@/types'

interface ThemeState {
  mode: ThemeMode
  setMode: (mode: ThemeMode) => void
  toggleTheme: () => void
}

function getSystemTheme(): 'light' | 'dark' {
  if (typeof window !== 'undefined') {
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
  }
  return 'light'
}

function applyTheme(mode: ThemeMode) {
  if (typeof document === 'undefined') return

  const root = document.documentElement
  const effectiveTheme = mode === 'system' ? getSystemTheme() : mode

  if (effectiveTheme === 'dark') {
    root.classList.add('dark')
  } else {
    root.classList.remove('dark')
  }
}

// Get initial theme from localStorage or default to 'system'
function getInitialTheme(): ThemeMode {
  if (typeof localStorage !== 'undefined') {
    const stored = localStorage.getItem('theme') as ThemeMode | null
    if (stored && ['light', 'dark', 'system'].includes(stored)) {
      return stored
    }
  }
  return 'system'
}

export const useThemeStore = create<ThemeState>((set, get) => {
  // Apply initial theme
  const initialMode = getInitialTheme()
  setTimeout(() => applyTheme(initialMode), 0)

  return {
    mode: initialMode,

    setMode: (mode: ThemeMode) => {
      localStorage.setItem('theme', mode)
      applyTheme(mode)
      set({ mode })
    },

    toggleTheme: () => {
      const { mode } = get()
      const currentEffective = mode === 'system' ? getSystemTheme() : mode
      const newMode: ThemeMode = currentEffective === 'dark' ? 'light' : 'dark'
      localStorage.setItem('theme', newMode)
      applyTheme(newMode)
      set({ mode: newMode })
    },
  }
})

// Listen for system theme changes
if (typeof window !== 'undefined') {
  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
    const store = useThemeStore.getState()
    if (store.mode === 'system') {
      applyTheme('system')
    }
  })
}
