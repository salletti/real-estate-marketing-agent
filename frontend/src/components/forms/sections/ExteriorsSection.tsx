import type { UseFormReturn } from 'react-hook-form'
import { FormField, FormItem, FormLabel, FormControl, FormMessage } from '@/components/ui/form'
import { Input } from '@/components/ui/input'
import { FormSection } from '@/components/forms/FormSection'
import type { PropertyFormValues } from '@/lib/validators/property.schema'

interface ExteriorsSectionProps {
  form: UseFormReturn<PropertyFormValues>
}

export function ExteriorsSection({ form }: ExteriorsSectionProps) {
  return (
    <FormSection title="Extérieurs & stationnement">
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <FormField
          control={form.control}
          name="balcony_count"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Balcons</FormLabel>
              <FormControl>
                <Input type="number" min="0" placeholder="0" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <FormField
          control={form.control}
          name="terrace_count"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Terrasses</FormLabel>
              <FormControl>
                <Input type="number" min="0" placeholder="0" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <FormField
          control={form.control}
          name="numberOfParkings"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Parkings</FormLabel>
              <FormControl>
                <Input type="number" min="0" placeholder="0" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
      </div>
    </FormSection>
  )
}
