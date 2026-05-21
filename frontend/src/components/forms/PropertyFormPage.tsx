import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { Form } from '@/components/ui/form'
import { Button } from '@/components/ui/button'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Loader2, AlertCircle, Sparkles } from 'lucide-react'
import { propertyFormSchema, type PropertyFormValues } from '@/lib/validators/property.schema'
import { useGenerateDraft } from '@/lib/hooks/useDraft'
import { GeneratingOverlay } from '@/components/forms/GeneratingOverlay'
import { SocialMediaSection } from '@/components/forms/sections/SocialMediaSection'
import { GeneralInfoSection } from '@/components/forms/sections/GeneralInfoSection'
import { LocationSection } from '@/components/forms/sections/LocationSection'
import { CharacteristicsSection } from '@/components/forms/sections/CharacteristicsSection'
import { ExteriorsSection } from '@/components/forms/sections/ExteriorsSection'
import { PhotosSection } from '@/components/forms/sections/PhotosSection'
import { AmenitiesSection } from '@/components/forms/sections/AmenitiesSection'

export function PropertyFormPage() {
  const generateDraft = useGenerateDraft()

  const form = useForm<PropertyFormValues>({
    resolver: zodResolver(propertyFormSchema),
    defaultValues: {
      userPrompt: '',
      platforms: ['facebook', 'instagram'],
      description: '',
      property_type: 'apartment',
      sub_type: '',
      transaction_type: 'sale',
      mandate_price: 0,
      charges: 0,
      taxes: 0,
      is_prestige: false,
      city: '',
      postalCode: '',
      country: 'France',
      surfaceArea: 0,
      roomsCount: 0,
      numberOfBedrooms: 0,
      overall_condition: 'good',
      work_required: false,
      exposures: ['south'],
      balcony_count: 0,
      terrace_count: 0,
      numberOfParkings: 0,
      photos: [],
      comfort: [],
      security: [],
      heatingSystem: [],
      heatingPowerSupply: [],
      heatingDistribution: [],
      residence: false,
      closedResidence: false,
    },
  })

  function onSubmit(values: PropertyFormValues) {
    generateDraft.mutate(values)
  }

  return (
    <>
      {generateDraft.isPending && <GeneratingOverlay />}

      <div className="mx-auto max-w-3xl px-4 py-10">
        <div className="mb-8">
          <div className="flex items-center gap-2 text-sm font-medium text-muted-foreground">
            <Sparkles className="h-4 w-4" />
            Agent IA Marketing Immobilier
          </div>
          <h1 className="mt-2 text-2xl font-semibold tracking-tight">
            Nouvelle publication
          </h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Renseignez les données du bien. L&apos;agent LangGraph générera les drafts pour review.
          </p>
        </div>

        {generateDraft.isError && (
          <Alert variant="destructive" className="mb-6">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>
              {generateDraft.error instanceof Error
                ? generateDraft.error.message
                : 'Erreur lors de la génération. Vérifiez que le backend est démarré.'}
            </AlertDescription>
          </Alert>
        )}

        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
            <SocialMediaSection form={form} />
            <GeneralInfoSection form={form} />
            <LocationSection form={form} />
            <CharacteristicsSection form={form} />
            <ExteriorsSection form={form} />
            <PhotosSection form={form} />
            <AmenitiesSection form={form} />

            <div className="flex justify-end pt-2">
              <Button
                type="submit"
                disabled={generateDraft.isPending}
                size="lg"
                className="min-w-40"
              >
                {generateDraft.isPending ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Génération…
                  </>
                ) : (
                  <>
                    <Sparkles className="mr-2 h-4 w-4" />
                    Lancer l&apos;agent
                  </>
                )}
              </Button>
            </div>
          </form>
        </Form>
      </div>
    </>
  )
}
