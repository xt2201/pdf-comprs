import { useAppConfigStore } from '@/stores/appConfigStore'

export function Footer() {
  const { config } = useAppConfigStore()
  
  return (
    <footer className="border-t bg-background/80 backdrop-blur-lg">
      <div className="container mx-auto px-4 py-6">
        <div className="flex flex-col items-center justify-between gap-4 sm:flex-row">
          <p className="text-sm text-muted-foreground">
            {config?.name || 'PDF Compression Tool'} — {config?.description || 'document compression'}
          </p>
          <div className="flex items-center gap-4 text-sm text-muted-foreground">
            <span>Supports PNG, JPG, JPEG, BMP, TIFF, WEBP</span>
          </div>
        </div>
      </div>
    </footer>
  )
}
