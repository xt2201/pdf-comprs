import { useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { cn } from '@/lib/utils'

interface UploadZoneProps {
  onFilesAccepted: (files: File[]) => void
  accept: Record<string, string[]>
  multiple?: boolean
  disabled?: boolean
  className?: string
  title?: string
  description?: string
}

export function UploadZone({
  onFilesAccepted,
  accept,
  multiple = true,
  disabled = false,
  className,
  title = 'Drop files here',
  description = 'or click to browse',
}: UploadZoneProps) {
  const onDrop = useCallback(
    (acceptedFiles: File[]) => {
      if (acceptedFiles.length > 0) {
        onFilesAccepted(acceptedFiles)
      }
    },
    [onFilesAccepted]
  )

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept,
    multiple,
    disabled,
  })

  return (
    <div
      {...getRootProps()}
      className={cn(
        'drop-zone flex cursor-pointer flex-col items-center justify-center text-center transition-all duration-300',
        isDragActive && 'dragging',
        disabled && 'cursor-not-allowed opacity-50',
        className
      )}
    >
      <input {...getInputProps()} />
      
      {/* Upload Icon */}
      <div className="mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-primary/10">
        <svg
          className="h-8 w-8 text-primary"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
          <polyline points="17 8 12 3 7 8" />
          <line x1="12" x2="12" y1="3" y2="15" />
        </svg>
      </div>
      
      <h3 className="text-lg font-medium text-foreground">{title}</h3>
      <p className="mt-1 text-sm text-muted-foreground">{description}</p>
      
      {isDragActive && (
        <div className="mt-4 rounded-md bg-primary/10 px-4 py-2">
          <p className="text-sm font-medium text-primary">Release to upload</p>
        </div>
      )}
    </div>
  )
}
