import type { UseFormReturn } from 'react-hook-form'
import { FormField, FormItem, FormLabel, FormControl, FormMessage } from '@/components/ui/form'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Checkbox } from '@/components/ui/checkbox'
import { Label } from '@/components/ui/label'
import { FormSection } from '@/components/forms/FormSection'
import type { PropertyFormValues } from '@/lib/validators/property.schema'

interface GeneralInfoSectionProps {
  form: UseFormReturn<PropertyFormValues>
}

export function GeneralInfoSection({ form }: GeneralInfoSectionProps) {
  return (
    <FormSection title="Informations générales">
      <FormField
        control={form.control}
        name="description"
        render={({ field }) => (
          <FormItem>
            <FormLabel>Description du bien</FormLabel>
            <FormControl>
              <Textarea
                placeholder="Bel appartement familial lumineux, étage élevé, proche commerces…"
                className="min-h-[80px]"
                {...field}
              />
            </FormControl>
            <FormMessage />
          </FormItem>
        )}
      />

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <FormField
          control={form.control}
          name="property_type"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Type de bien</FormLabel>
              <Select onValueChange={field.onChange} defaultValue={field.value}>
                <FormControl>
                  <SelectTrigger>
                    <SelectValue placeholder="Sélectionner…" />
                  </SelectTrigger>
                </FormControl>
                <SelectContent>
                  <SelectItem value="apartment">Appartement</SelectItem>
                  <SelectItem value="house">Maison</SelectItem>
                  <SelectItem value="land">Terrain</SelectItem>
                  <SelectItem value="commercial">Local commercial</SelectItem>
                  <SelectItem value="parking">Parking</SelectItem>
                </SelectContent>
              </Select>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="sub_type"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Sous-type</FormLabel>
              <FormControl>
                <Input placeholder="T4, Villa, Studio, Duplex…" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="transaction_type"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Transaction</FormLabel>
              <Select onValueChange={field.onChange} defaultValue={field.value}>
                <FormControl>
                  <SelectTrigger>
                    <SelectValue placeholder="Sélectionner…" />
                  </SelectTrigger>
                </FormControl>
                <SelectContent>
                  <SelectItem value="sale">Vente</SelectItem>
                  <SelectItem value="rental">Location</SelectItem>
                </SelectContent>
              </Select>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="mandate_price"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Prix (€)</FormLabel>
              <FormControl>
                <Input type="number" placeholder="1290000" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="charges"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Charges mensuelles (€)</FormLabel>
              <FormControl>
                <Input type="number" placeholder="320" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="taxes"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Taxe foncière annuelle (€)</FormLabel>
              <FormControl>
                <Input type="number" placeholder="2100" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
      </div>

      <div className="flex items-center gap-2">
        <Checkbox
          id="is_prestige"
          checked={form.watch('is_prestige')}
          onCheckedChange={(checked) => form.setValue('is_prestige', !!checked)}
        />
        <Label htmlFor="is_prestige" className="cursor-pointer">
          Bien prestige
        </Label>
      </div>
    </FormSection>
  )
}
