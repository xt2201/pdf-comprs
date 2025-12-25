import { useState } from 'react'
import { useFileStore } from '@/stores/fileStore'
import { useCompressionStore } from '@/stores/compressionStore'
import { imagesToPdf } from '@/services/compressionApi'
import { FileList } from '@/components/upload/FileList'
import { SettingsForm } from './SettingsForm'
import { ResultDisplay } from './ResultDisplay'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'

export function ImageToPdfPanel() {
  const { imageFiles, settings } = useFileStore()
  const { isProcessing, setProcessing, setProgress, setResult, setError } = useCompressionStore()
  const [selectedImageId, setSelectedImageId] = useState<string>()

  const selectedImage = imageFiles.find((f) => f.id === selectedImageId)

  const handleProcess = async () => {
    if (imageFiles.length === 0) return

    setProcessing(true)
    setProgress(0)

    try {
      // Sort files by order
      const sortedFiles = [...imageFiles].sort((a, b) => a.order - b.order)
      const files = sortedFiles.map((f) => f.file)

      const result = await imagesToPdf(files, settings, (progress) => {
        setProgress(Math.min(progress, 90))
      })

      setResult(result)
    } catch (err) {
      const error = err as { message?: string }
      setError(error.message || 'Failed to create PDF')
    }
  }

  return (
    <div className="grid gap-6 lg:grid-cols-3">
      {/* Left Column - File List & Settings */}
      <div className="space-y-6 lg:col-span-2">
        <FileList onPreviewSelect={setSelectedImageId} selectedId={selectedImageId} />
        <SettingsForm />
        
        {/* Process Button */}
        <Button
          onClick={handleProcess}
          disabled={imageFiles.length === 0 || isProcessing}
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
              Processing...
            </>
          ) : (
            <>
              Create & Compress PDF
            </>
          )}
        </Button>
      </div>

      {/* Right Column - Preview & Result */}
      <div className="space-y-6">
        {/* Image Preview */}
        <Card className="glass-strong">
          <CardContent className="p-4">
            {selectedImage?.preview ? (
              <img
                src={selectedImage.preview}
                alt={selectedImage.file.name}
                className="w-full rounded-lg object-contain"
                style={{ maxHeight: '300px' }}
              />
            ) : (
              <div className="flex h-[200px] items-center justify-center rounded-lg bg-muted">
                <p className="text-sm text-muted-foreground">
                  Select an image to preview
                </p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Result Display */}
        <ResultDisplay />
      </div>
    </div>
  )
}
