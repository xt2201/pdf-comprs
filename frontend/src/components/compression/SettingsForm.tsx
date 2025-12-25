import { useFileStore } from '@/stores/fileStore'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Label } from '@/components/ui/label'
import { Slider } from '@/components/ui/slider'
import { Switch } from '@/components/ui/switch'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'

interface SettingsFormProps {
  showAutoCompress?: boolean
}

export function SettingsForm({ showAutoCompress = true }: SettingsFormProps) {
  const { settings, updateSettings } = useFileStore()

  const presets = [
    { name: 'High Quality', dpi: 150, quality: 80 },
    { name: 'Medium', dpi: 96, quality: 60 },
    { name: 'Low Size', dpi: 50, quality: 30 },
  ]

  const applyPreset = (preset: { dpi: number; quality: number }) => {
    updateSettings({
      dpi: preset.dpi,
      quality: preset.quality,
      autoCompress: false,
    })
  }

  return (
    <Card className="glass-strong">
      <CardHeader>
        <CardTitle className="text-lg font-semibold">Compression Settings</CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Output Filename */}
        <div className="space-y-2">
          <Label htmlFor="filename">Output Filename</Label>
          <Input
            id="filename"
            value={settings.outputFilename}
            onChange={(e) => updateSettings({ outputFilename: e.target.value })}
            placeholder="Enter filename"
          />
        </div>

        {/* Auto Compress Toggle */}
        {showAutoCompress && (
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label htmlFor="auto-compress">Auto Compress</Label>
              <p className="text-sm text-muted-foreground">
                Automatically find best settings to reach target size
              </p>
            </div>
            <Switch
              id="auto-compress"
              checked={settings.autoCompress}
              onCheckedChange={(checked) => updateSettings({ autoCompress: checked })}
            />
          </div>
        )}

        {/* Target Size */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <Label>Target Size</Label>
            <span className="text-sm font-medium text-primary">
              {settings.targetSizeMb.toFixed(1)} MB
            </span>
          </div>
          <Slider
            value={[settings.targetSizeMb]}
            onValueChange={([value]) => updateSettings({ targetSizeMb: value })}
            min={0.1}
            max={10}
            step={0.1}
          />
        </div>

        {/* Manual Settings (shown when auto is off) */}
        {!settings.autoCompress && (
          <>
            {/* DPI */}
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <Label>DPI (Resolution)</Label>
                <span className="text-sm font-medium text-primary">{settings.dpi}</span>
              </div>
              <Slider
                value={[settings.dpi]}
                onValueChange={([value]) => updateSettings({ dpi: value })}
                min={10}
                max={300}
                step={5}
              />
            </div>

            {/* Quality */}
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <Label>JPEG Quality</Label>
                <span className="text-sm font-medium text-primary">{settings.quality}%</span>
              </div>
              <Slider
                value={[settings.quality]}
                onValueChange={([value]) => updateSettings({ quality: value })}
                min={5}
                max={100}
                step={5}
              />
            </div>

            {/* Quick Presets */}
            <div className="space-y-2">
              <Label>Quick Presets</Label>
              <div className="flex flex-wrap gap-2">
                {presets.map((preset) => (
                  <Button
                    key={preset.name}
                    variant="outline"
                    size="sm"
                    onClick={() => applyPreset(preset)}
                  >
                    {preset.name}
                  </Button>
                ))}
              </div>
            </div>
          </>
        )}
      </CardContent>
    </Card>
  )
}
