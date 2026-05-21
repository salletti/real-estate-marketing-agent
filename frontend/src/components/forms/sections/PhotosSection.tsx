import type { UseFormReturn } from 'react-hook-form'
import { Plus, Trash2, ImageIcon } from 'lucide-react'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { FormSection } from '@/components/forms/FormSection'
import type { PropertyFormValues } from '@/lib/validators/property.schema'

interface PhotosSectionProps {
  form: UseFormReturn<PropertyFormValues>
}

export function PhotosSection({ form }: PhotosSectionProps) {
  const photos = form.watch('photos')

  const updatePhoto = (index: number, value: string) => {
    const updated = [...photos]
    updated[index] = value
    form.setValue('photos', updated, { shouldValidate: true })
  }

  const removePhoto = (index: number) => {
    form.setValue('photos', photos.filter((_, i) => i !== index), { shouldValidate: true })
  }

  const addPhoto = () => {
    form.setValue('photos', [...photos, ''])
  }

  return (
    <FormSection title="Photos">
      <div className="space-y-2">
        {photos.length === 0 && (
          <div className="flex items-center gap-2 rounded-lg border border-dashed p-4 text-sm text-muted-foreground">
            <ImageIcon className="h-4 w-4 shrink-0" />
            Aucune photo — ajoutez des URLs pour enrichir les posts générés
          </div>
        )}

        {photos.map((url, index) => (
          <div key={index} className="flex gap-2">
            <Input
              type="url"
              placeholder="https://images.example.com/photo.jpg"
              value={url}
              onChange={(e) => updatePhoto(index, e.target.value)}
              className="flex-1"
            />
            <Button
              type="button"
              variant="ghost"
              size="icon"
              onClick={() => removePhoto(index)}
            >
              <Trash2 className="h-4 w-4 text-destructive" />
            </Button>
          </div>
        ))}

        {photos.length > 0 && form.formState.errors.photos && (
          <p className="text-sm text-destructive">
            {typeof form.formState.errors.photos === 'object' &&
              Object.values(form.formState.errors.photos)
                .map((e) => (e as { message?: string })?.message)
                .filter(Boolean)
                .join(', ')}
          </p>
        )}

        <Button
          type="button"
          variant="outline"
          size="sm"
          className="gap-2 mt-1"
          onClick={addPhoto}
        >
          <Plus className="h-4 w-4" />
          Ajouter une photo
        </Button>
      </div>
    </FormSection>
  )
}
