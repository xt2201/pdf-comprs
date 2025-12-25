import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Progress } from '@/components/ui/progress'
import { useCompressionStore } from '@/stores/compressionStore'
import { downloadFile } from '@/services/compressionApi'
import { cn } from '@/lib/utils'
import { PdfPreview } from './PdfPreview'

export function ResultDisplay() {
  const { isProcessing, progress, result, error, reset } = useCompressionStore()

  if (!isProcessing && !result && !error) {
    return null
  }

  const handleDownload = async () => {
    if (result && 'downloadUrl' in result) {
      const filename = result.downloadUrl.split('/').pop() || 'compressed.pdf'
      try {
        await downloadFile(result.jobId, filename)
      } catch (e) {
        console.error('Download failed:', e)
      }
    }
  }

  return (
    <Card className={cn(
      'glass-strong',
      error && 'border-destructive',
      result?.success && 'border-green-500'
    )}>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4">
        <CardTitle className="text-lg font-semibold">
          {isProcessing ? 'Processing...' : error ? 'Error' : 'Result'}
        </CardTitle>
        {(result || error) && (
          <Button variant="ghost" size="sm" onClick={reset}>
            Clear
          </Button>
        )}
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Progress */}
        {isProcessing && (
          <div className="space-y-2">
            <Progress value={progress} className="h-2" />
            <p className="text-center text-sm text-muted-foreground">
              {progress}% complete
            </p>
          </div>
        )}

        {/* Error */}
        {error && (
          <div className="rounded-lg bg-destructive/10 p-4">
            <p className="text-sm text-destructive">{error}</p>
          </div>
        )}

        {/* Success Result */}
        {result && result.success && (
          <div className="space-y-4">
            {/* Stats Grid */}
            <div className="grid grid-cols-2 gap-4">
              <div className="rounded-lg bg-muted p-3">
                <p className="text-xs text-muted-foreground">Original Size</p>
                <p className="text-lg font-semibold">
                  {(result.originalSizeMb ?? 0).toFixed(2)} MB
                </p>
              </div>
              <div className="rounded-lg bg-muted p-3">
                <p className="text-xs text-muted-foreground">Compressed Size</p>
                <p className="text-lg font-semibold text-primary">
                  {(result.compressedSizeMb ?? 0).toFixed(2)} MB
                </p>
              </div>
            </div>

            {/* Reduction */}
            <div className="rounded-lg bg-green-500/10 p-4 text-center">
              <p className="text-sm text-muted-foreground">Size Reduction</p>
              <p className="text-3xl font-bold text-green-600">
                {(result.reductionPercent ?? 0).toFixed(1)}%
              </p>
            </div>

            {/* Config Used */}
            {'configUsed' in result && result.configUsed && (
              <div className="text-center text-sm text-muted-foreground">
                Settings: {result.configUsed.description} ({result.configUsed.dpi} DPI,{' '}
                {result.configUsed.quality}% quality)
              </div>
            )}

            {/* PDF Preview - Always shown */}
            <div className="mt-4">
              <PdfPreview jobId={result.jobId} />
            </div>

            {/* Download Button */}
            <Button onClick={handleDownload} className="w-full" size="lg">
              <svg
                className="mr-2 h-4 w-4"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                <polyline points="7 10 12 15 17 10" />
                <line x1="12" x2="12" y1="15" y2="3" />
              </svg>
              Download PDF
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
