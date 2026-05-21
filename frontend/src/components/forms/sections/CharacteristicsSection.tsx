import type { UseFormReturn } from 'react-hook-form'
import { FormField, FormItem, FormLabel, FormControl, FormMessage } from '@/components/ui/form'
import { Input } from '@/components/ui/input'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Checkbox } from '@/components/ui/checkbox'
import { Label } from '@/components/ui/label'
import { CheckboxGroup } from '@/components/forms/CheckboxGroup'
import { FormSection } from '@/components/forms/FormSection'
import { EXPOSURE_OPTIONS } from '@/lib/validators/property.schema'
import type { PropertyFormValues } from '@/lib/validators/property.schema'

const EXPOSURE_LABELS: Record<string, string> = {
  north: 'Nord', south: 'Sud', east: 'Est', west: 'Ouest',
}

interface CharacteristicsSectionProps {
  form: UseFormReturn<PropertyFormValues>
}

export function CharacteristicsSection({ form }: CharacteristicsSectionProps) {
  return (
    <FormSection title="Caractéristiques">
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <FormField
          control={form.control}
          name="surfaceArea"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Surface (m²)</FormLabel>
              <FormControl>
                <Input type="number" placeholder="112" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <FormField
          control={form.control}
          name="roomsCount"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Nombre de pièces</FormLabel>
              <FormControl>
                <Input type="number" placeholder="4" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <FormField
          control={form.control}
          name="numberOfBedrooms"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Chambres</FormLabel>
              <FormControl>
                <Input type="number" placeholder="3" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
      </div>

      <FormField
        control={form.control}
        name="overall_condition"
        render={({ field }) => (
          <FormItem>
            <FormLabel>État général</FormLabel>
            <Select onValueChange={field.onChange} defaultValue={field.value}>
              <FormControl>
                <SelectTrigger className="w-48">
                  <SelectValue placeholder="Sélectionner…" />
                </SelectTrigger>
              </FormControl>
              <SelectContent>
                <SelectItem value="excellent">Excellent</SelectItem>
                <SelectItem value="good">Bon</SelectItem>
                <SelectItem value="fair">Correct</SelectItem>
                <SelectItem value="poor">À rénover</SelectItem>
              </SelectContent>
            </Select>
            <FormMessage />
          </FormItem>
        )}
      />

      <div className="flex items-center gap-2">
        <Checkbox
          id="work_required"
          checked={form.watch('work_required')}
          onCheckedChange={(checked) => form.setValue('work_required', !!checked)}
        />
        <Label htmlFor="work_required" className="cursor-pointer">
          Travaux nécessaires
        </Label>
      </div>

      <FormField
        control={form.control}
        name="exposures"
        render={({ field }) => (
          <FormItem>
            <FormLabel>Exposition</FormLabel>
            <FormControl>
              <CheckboxGroup
                options={EXPOSURE_OPTIONS}
                value={field.value}
                onChange={field.onChange}
                labelMap={EXPOSURE_LABELS}
              />
            </FormControl>
            <FormMessage />
          </FormItem>
        )}
      />
    </FormSection>
  )
}
