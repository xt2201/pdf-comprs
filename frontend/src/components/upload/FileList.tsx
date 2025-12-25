import { useState } from 'react'
import {
  DndContext,
  closestCenter,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
  DragEndEvent,
} from '@dnd-kit/core'
import {
  SortableContext,
  sortableKeyboardCoordinates,
  verticalListSortingStrategy,
} from '@dnd-kit/sortable'
import { useFileStore } from '@/stores/fileStore'
import { ImageItem } from './ImageItem'
import { UploadZone } from './UploadZone'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { formatFileSize } from '@/lib/utils'

interface FileListProps {
  onPreviewSelect?: (id: string) => void
  selectedId?: string
}

export function FileList({ onPreviewSelect, selectedId }: FileListProps) {
  const { imageFiles, addImageFiles, removeImageFile, reorderImageFiles, clearImageFiles } =
    useFileStore()

  const sensors = useSensors(
    useSensor(PointerSensor),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    })
  )

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event
    if (over && active.id !== over.id) {
      reorderImageFiles(active.id as string, over.id as string)
    }
  }

  const handleFilesAccepted = (files: File[]) => {
    addImageFiles(files)
  }

  const totalSize = imageFiles.reduce((sum, f) => sum + f.file.size, 0)

  return (
    <Card className="glass-strong">
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4">
        <CardTitle className="text-lg font-semibold">Images</CardTitle>
        {imageFiles.length > 0 && (
          <div className="flex items-center gap-2">
            <span className="text-sm text-muted-foreground">
              {imageFiles.length} file{imageFiles.length !== 1 ? 's' : ''} • {formatFileSize(totalSize)}
            </span>
            <Button variant="ghost" size="sm" onClick={clearImageFiles}>
              Clear all
            </Button>
          </div>
        )}
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Upload Zone */}
        <UploadZone
          onFilesAccepted={handleFilesAccepted}
          accept={{
            'image/png': ['.png'],
            'image/jpeg': ['.jpg', '.jpeg'],
            'image/bmp': ['.bmp'],
            'image/tiff': ['.tiff', '.tif'],
            'image/webp': ['.webp'],
          }}
          multiple
          title="Drop images here"
          description="PNG, JPG, BMP, TIFF, WEBP"
          className="min-h-[120px]"
        />

        {/* File List */}
        {imageFiles.length > 0 && (
          <div className="max-h-[400px] space-y-2 overflow-y-auto pr-2">
            <DndContext
              sensors={sensors}
              collisionDetection={closestCenter}
              onDragEnd={handleDragEnd}
            >
              <SortableContext
                items={imageFiles.map((f) => f.id)}
                strategy={verticalListSortingStrategy}
              >
                {imageFiles.map((file, index) => (
                  <ImageItem
                    key={file.id}
                    file={file}
                    index={index}
                    onRemove={removeImageFile}
                    isSelected={selectedId === file.id}
                    onSelect={onPreviewSelect}
                  />
                ))}
              </SortableContext>
            </DndContext>
          </div>
        )}

        {imageFiles.length === 0 && (
          <p className="text-center text-sm text-muted-foreground py-4">
            No images uploaded. Drag and drop to add files.
          </p>
        )}
      </CardContent>
    </Card>
  )
}
