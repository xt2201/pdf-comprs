import axios, { AxiosError, AxiosInstance } from 'axios'
import type { ApiError } from '@/types'

// Create axios instance with base configuration
const api: AxiosInstance = axios.create({
  baseURL: '/api',
  timeout: 300000, // 5 minutes for large file uploads
  headers: {
    'Accept': 'application/json',
  },
})

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error: AxiosError<{ error?: ApiError; detail?: ApiError }>) => {
    const errorData = error.response?.data
    const apiError: ApiError = {
      code: errorData?.error?.code || errorData?.detail?.code || 'UNKNOWN_ERROR',
      message: errorData?.error?.message || errorData?.detail?.message || error.message || 'An unexpected error occurred',
    }
    return Promise.reject(apiError)
  }
)

export default api
