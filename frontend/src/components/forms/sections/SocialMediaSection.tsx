import type { UseFormReturn } from 'react-hook-form'
import { FormField, FormItem, FormLabel, FormControl, FormMessage } from '@/components/ui/form'
import { Textarea } from '@/components/ui/textarea'
import { CheckboxGroup } from '@/components/forms/CheckboxGroup'
import { FormSection } from '@/components/forms/FormSection'
import { PLATFORM_OPTIONS } from '@/lib/validators/property.schema'
import type { PropertyFormValues } from '@/lib/validators/property.schema'

const PLATFORM_LABELS: Record<string, string> = {
  facebook: 'Facebook',
  instagram: 'Instagram',
}

interface SocialMediaSectionProps {
  form: UseFormReturn<PropertyFormValues>
}

export function SocialMediaSection({ form }: SocialMediaSectionProps) {
  return (
    <FormSection title="Réseaux sociaux">
      <FormField
        control={form.control}
        name="platforms"
        render={({ field }) => (
          <FormItem>
            <FormLabel>Plateformes cibles</FormLabel>
            <FormControl>
              <CheckboxGroup
                options={PLATFORM_OPTIONS}
                value={field.value}
                onChange={field.onChange}
                labelMap={PLATFORM_LABELS}
              />
            </FormControl>
            <FormMessage />
          </FormItem>
        )}
      />
      <FormField
        control={form.control}
        name="userPrompt"
        render={({ field }) => (
          <FormItem>
            <FormLabel>Instructions pour l&apos;agent</FormLabel>
            <FormControl>
              <Textarea
                placeholder="Ex: Ton professionnel et chaleureux, mets en avant le balcon et la luminosité, appel à l'action pour une visite…"
                className="min-h-[100px]"
                {...field}
              />
            </FormControl>
            <FormMessage />
          </FormItem>
        )}
      />
    </FormSection>
  )
}
