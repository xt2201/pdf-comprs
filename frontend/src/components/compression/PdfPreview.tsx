import { useState } from 'react'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'

interface PdfPreviewProps {
  jobId: string
  className?: string
}

export function PdfPreview({ jobId, className }: PdfPreviewProps) {
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [scale, setScale] = useState(100)

  const previewUrl = `/api/compress/preview/${jobId}`

  const handleLoad = () => {
    setIsLoading(false)
    setError(null)
  }

  const handleError = () => {
    setIsLoading(false)
    setError('Failed to load PDF preview')
  }

  const handleZoomIn = () => {
    setScale((prev) => Math.min(prev + 25, 200))
  }

  const handleZoomOut = () => {
    setScale((prev) => Math.max(prev - 25, 50))
  }

  const handleZoomReset = () => {
    setScale(100)
  }

  return (
    <Card className={cn('overflow-hidden', className)}>
      <CardContent className="p-0">
        {/* Toolbar */}
        <div className="flex items-center justify-between border-b bg-muted/50 px-4 py-2">
          <div className="flex items-center gap-2">
            <span className="text-sm font-medium text-muted-foreground">Preview</span>
            {isLoading && (
              <span className="text-xs text-muted-foreground">Loading...</span>
            )}
          </div>
          <div className="flex items-center gap-1">
            <Button
              variant="ghost"
              size="sm"
              onClick={handleZoomOut}
              disabled={scale <= 50}
              className="h-8 w-8 p-0"
              title="Zoom out"
            >
              <svg
                className="h-4 w-4"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
              >
                <circle cx="11" cy="11" r="8" />
                <path d="M21 21l-4.35-4.35" />
                <line x1="8" x2="14" y1="11" y2="11" />
              </svg>
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={handleZoomReset}
              className="h-8 px-2 text-xs"
              title="Reset zoom"
            >
              {scale}%
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={handleZoomIn}
              disabled={scale >= 200}
              className="h-8 w-8 p-0"
              title="Zoom in"
            >
              <svg
                className="h-4 w-4"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
              >
                <circle cx="11" cy="11" r="8" />
                <path d="M21 21l-4.35-4.35" />
                <line x1="11" x2="11" y1="8" y2="14" />
                <line x1="8" x2="14" y1="11" y2="11" />
              </svg>
            </Button>
          </div>
        </div>

        {/* Preview Container */}
        <div className="relative bg-muted/30" style={{ height: '600px' }}>
          {error ? (
            <div className="flex h-full items-center justify-center">
              <div className="text-center">
                <svg
                  className="mx-auto h-12 w-12 text-destructive"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                >
                  <circle cx="12" cy="12" r="10" />
                  <line x1="12" x2="12" y1="8" y2="12" />
                  <line x1="12" x2="12.01" y1="16" y2="16" />
                </svg>
                <p className="mt-2 text-sm text-destructive">{error}</p>
              </div>
            </div>
          ) : (
            <>
              {isLoading && (
                <div className="absolute inset-0 z-10 flex items-center justify-center bg-background/80">
                  <div className="flex flex-col items-center gap-2">
                    <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
                    <span className="text-sm text-muted-foreground">Loading PDF...</span>
                  </div>
                </div>
              )}
              <div className="h-full overflow-auto p-4">
                <div
                  className="mx-auto transition-transform"
                  style={{
                    transform: `scale(${scale / 100})`,
                    transformOrigin: 'top center',
                  }}
                >
                  <iframe
                    src={previewUrl}
                    className="w-full rounded border bg-white shadow-lg"
                    style={{ height: '800px', minWidth: '600px' }}
                    onLoad={handleLoad}
                    onError={handleError}
                    title="PDF Preview"
                  />
                </div>
              </div>
            </>
          )}
        </div>
      </CardContent>
    </Card>
  )
}
