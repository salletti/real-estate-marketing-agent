import type { UseFormReturn } from 'react-hook-form'
import { FormField, FormItem, FormLabel, FormControl, FormMessage } from '@/components/ui/form'
import { Checkbox } from '@/components/ui/checkbox'
import { Label } from '@/components/ui/label'
import { CheckboxGroup } from '@/components/forms/CheckboxGroup'
import { FormSection } from '@/components/forms/FormSection'
import {
  COMFORT_OPTIONS,
  SECURITY_OPTIONS,
  HEATING_SYSTEM_OPTIONS,
  HEATING_POWER_OPTIONS,
  HEATING_DISTRIBUTION_OPTIONS,
} from '@/lib/validators/property.schema'
import type { PropertyFormValues } from '@/lib/validators/property.schema'

interface AmenitiesSectionProps {
  form: UseFormReturn<PropertyFormValues>
}

export function AmenitiesSection({ form }: AmenitiesSectionProps) {
  return (
    <FormSection title="Équipements & confort">
      <FormField
        control={form.control}
        name="comfort"
        render={({ field }) => (
          <FormItem>
            <FormLabel>Confort</FormLabel>
            <FormControl>
              <CheckboxGroup options={COMFORT_OPTIONS} value={field.value} onChange={field.onChange} />
            </FormControl>
            <FormMessage />
          </FormItem>
        )}
      />

      <FormField
        control={form.control}
        name="security"
        render={({ field }) => (
          <FormItem>
            <FormLabel>Sécurité</FormLabel>
            <FormControl>
              <CheckboxGroup options={SECURITY_OPTIONS} value={field.value} onChange={field.onChange} />
            </FormControl>
            <FormMessage />
          </FormItem>
        )}
      />

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <FormField
          control={form.control}
          name="heatingSystem"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Système de chauffage</FormLabel>
              <FormControl>
                <CheckboxGroup options={HEATING_SYSTEM_OPTIONS} value={field.value} onChange={field.onChange} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <FormField
          control={form.control}
          name="heatingPowerSupply"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Énergie</FormLabel>
              <FormControl>
                <CheckboxGroup options={HEATING_POWER_OPTIONS} value={field.value} onChange={field.onChange} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <FormField
          control={form.control}
          name="heatingDistribution"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Distribution</FormLabel>
              <FormControl>
                <CheckboxGroup options={HEATING_DISTRIBUTION_OPTIONS} value={field.value} onChange={field.onChange} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
      </div>

      <div className="flex gap-6">
        <div className="flex items-center gap-2">
          <Checkbox
            id="residence"
            checked={form.watch('residence')}
            onCheckedChange={(checked) => form.setValue('residence', !!checked)}
          />
          <Label htmlFor="residence" className="cursor-pointer">En résidence</Label>
        </div>
        <div className="flex items-center gap-2">
          <Checkbox
            id="closedResidence"
            checked={form.watch('closedResidence')}
            onCheckedChange={(checked) => form.setValue('closedResidence', !!checked)}
          />
          <Label htmlFor="closedResidence" className="cursor-pointer">Résidence fermée</Label>
        </div>
      </div>
    </FormSection>
  )
}
