import { useFileStore } from '@/stores/fileStore'
import { useCompressionStore } from '@/stores/compressionStore'
import { compressPdf } from '@/services/compressionApi'
import { UploadZone } from '@/components/upload/UploadZone'
import { SettingsForm } from './SettingsForm'
import { ResultDisplay } from './ResultDisplay'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { formatFileSize } from '@/lib/utils'

export function CompressPdfPanel() {
  const { pdfFile, setPdfFile, clearPdfFile, settings } = useFileStore()
  const { isProcessing, setProcessing, setProgress, setResult, setError } = useCompressionStore()

  const handleFileAccepted = (files: File[]) => {
    if (files.length > 0) {
      setPdfFile(files[0])
    }
  }

  const handleProcess = async () => {
    if (!pdfFile) return

    setProcessing(true)
    setProgress(0)

    try {
      const result = await compressPdf(pdfFile, settings, (progress) => {
        setProgress(Math.min(progress, 90))
      })

      setResult(result)
    } catch (err) {
      const error = err as { message?: string }
      setError(error.message || 'Failed to compress PDF')
    }
  }

  return (
    <div className="grid gap-6 lg:grid-cols-3">
      {/* Left Column - Upload & Settings */}
      <div className="space-y-6 lg:col-span-2">
        {/* PDF Upload */}
        <Card className="glass-strong">
          <CardHeader>
            <CardTitle className="text-lg font-semibold">PDF File</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {!pdfFile ? (
              <UploadZone
                onFilesAccepted={handleFileAccepted}
                accept={{ 'application/pdf': ['.pdf'] }}
                multiple={false}
                title="Drop PDF here"
                description="or click to browse"
                className="min-h-[150px]"
              />
            ) : (
              <div className="flex items-center justify-between rounded-lg border bg-card p-4">
                <div className="flex items-center gap-3">
                  {/* PDF Icon */}
                  <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10">
                    <svg
                      className="h-6 w-6 text-primary"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="2"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    >
                      <path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z" />
                      <polyline points="14 2 14 8 20 8" />
                    </svg>
                  </div>
                  <div>
                    <p className="font-medium text-foreground">{pdfFile.name}</p>
                    <p className="text-sm text-muted-foreground">
                      {formatFileSize(pdfFile.size)}
                    </p>
                  </div>
                </div>
                <Button variant="ghost" size="sm" onClick={clearPdfFile}>
                  Remove
                </Button>
              </div>
            )}
          </CardContent>
        </Card>

        <SettingsForm />

        {/* Process Button */}
        <Button
          onClick={handleProcess}
          disabled={!pdfFile || isProcessing}
          className="w-full"
          size="xl"
        >
          {isProcessing ? (
            <>
              <svg
                className="mr-2 h-4 w-4 animate-spin"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
              >
                <path d="M21 12a9 9 0 1 1-6.219-8.56" />
              </svg>
              Compressing...
            </>
          ) : (
            'Compress PDF'
          )}
        </Button>
      </div>

      {/* Right Column - Result */}
      <div className="space-y-6">
        <ResultDisplay />
        
        {/* Tips Card */}
        <Card className="glass-strong">
          <CardHeader>
            <CardTitle className="text-lg font-semibold">Tips</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2 text-sm text-muted-foreground">
            <p>Lower DPI and quality values result in smaller file sizes but reduced visual quality.</p>
            <p>Enable Auto Compress to automatically find the best settings to reach your target size.</p>
            <p>For documents with mostly text, lower DPI has minimal visual impact.</p>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
