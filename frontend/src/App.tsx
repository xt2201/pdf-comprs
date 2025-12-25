import { MainLayout } from '@/components/layout/MainLayout'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { ImageToPdfPanel } from '@/components/compression/ImageToPdfPanel'
import { CompressPdfPanel } from '@/components/compression/CompressPdfPanel'
import { useFileStore } from '@/stores/fileStore'
import { useCompressionStore } from '@/stores/compressionStore'
import { useAppConfigStore } from '@/stores/appConfigStore'
import { useEffect } from 'react'

function App() {
  const { clearImageFiles, clearPdfFile, resetSettings } = useFileStore()
  const { reset: resetCompression } = useCompressionStore()
  const { config, fetchConfig } = useAppConfigStore()

  useEffect(() => {
    fetchConfig()
  }, [])

  useEffect(() => {
    if (config?.title) {
      document.title = config.title
    }
  }, [config])

  const handleTabChange = () => {
    // Reset state when switching tabs
    clearImageFiles()
    clearPdfFile()
    resetSettings()
    resetCompression()
  }

  return (
    <MainLayout>
      <div className="mx-auto max-w-6xl">
        {/* Hero Section */}
        <div className="mb-8 text-center">
          <h1 className="text-4xl font-bold tracking-tight sm:text-5xl">
            <span className="text-gradient">{config?.name || 'PDF Compression Tool'}</span>
          </h1>
          <p className="mt-4 text-lg text-muted-foreground">
            {config?.description || 'Convert images to PDF and compress with professional quality settings'}
          </p>
        </div>

        {/* Main Tabs */}
        <Tabs defaultValue="images" onValueChange={handleTabChange}>
          <TabsList className="grid w-full grid-cols-2 lg:w-auto lg:inline-grid">
            <TabsTrigger value="images" className="px-8">
              Images to PDF
            </TabsTrigger>
            <TabsTrigger value="compress" className="px-8">
              Compress PDF
            </TabsTrigger>
          </TabsList>

          <TabsContent value="images">
            <ImageToPdfPanel />
          </TabsContent>

          <TabsContent value="compress">
            <CompressPdfPanel />
          </TabsContent>
        </Tabs>
      </div>
    </MainLayout>
  )
}

export default App
