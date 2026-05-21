import { request } from './client'
import { draftResponseSchema } from '@/lib/validators/draft.schema'
import type { DraftResponse, GenerateDraftRequest } from '@/lib/types/api'
import type { PropertyFormValues } from '@/lib/validators/property.schema'

export function buildGeneratePayload(values: PropertyFormValues): GenerateDraftRequest {
  const platformNames = values.platforms
    .map((p) => (p === 'facebook' ? 'Facebook' : 'Instagram'))
    .join(' et ')

  const input = `${values.userPrompt} Génère un post ${platformNames}.`

  return {
    input,
    property_json: {
      id: Math.floor(Math.random() * 90000) + 10000,
      uid: `${values.city.slice(0, 3).toUpperCase()}-${values.sub_type}-${Date.now()}`,
      property_type: values.property_type,
      sub_type: values.sub_type,
      transaction_type: values.transaction_type,
      location: {
        city: values.city,
        postalCode: values.postalCode,
        country: values.country,
      },
      living_area: {
        surfaceArea: values.surfaceArea,
        roomsCount: values.roomsCount,
        numberOfBedrooms: values.numberOfBedrooms,
      },
      mandate_price: values.mandate_price,
      charges: values.charges,
      taxes: values.taxes,
      description: values.description,
      balcony_count: values.balcony_count,
      terrace_count: values.terrace_count,
      overall_condition: values.overall_condition,
      work_required: values.work_required,
      environment: {
        hasPool: false,
        numberOfParkings: values.numberOfParkings,
      },
      co_ownership: {
        fee: values.charges,
      },
      amenities: {
        comfort: values.comfort,
        security: values.security,
        heatingSystem: values.heatingSystem,
        heatingPowerSupply: values.heatingPowerSupply,
        heatingDistribution: values.heatingDistribution,
        residence: values.residence,
        closedResidence: values.closedResidence,
      },
      exposures: values.exposures,
      is_prestige: values.is_prestige,
      photos: values.photos.map((url) => ({ url })),
      created_at: new Date().toISOString(),
    },
  }
}

function parseDraft(raw: unknown): DraftResponse {
  return draftResponseSchema.parse(raw) as DraftResponse
}

export async function generateDraft(payload: GenerateDraftRequest): Promise<DraftResponse> {
  const raw = await request<unknown>('/drafts/generate', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
  return parseDraft(raw)
}

export async function getDraft(threadId: string): Promise<DraftResponse> {
  const raw = await request<unknown>(`/drafts/${threadId}`)
  return parseDraft(raw)
}

export async function executeDraftAction(href: string, method: string): Promise<DraftResponse> {
  const raw = await request<unknown>(href, { method })
  return parseDraft(raw)
}
