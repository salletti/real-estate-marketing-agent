export interface LinkResponse {
  method: 'GET' | 'POST'
  href: string
}

export type DraftStatus = 'draft' | 'published' | 'rejected'
export type ApprovalStatus = 'pending' | 'approved' | 'rejected' | null

export interface FacebookPlatformContent {
  generated: true
  post: string
  hashtags: string[]
  images: string[]
}

export interface InstagramPlatformContent {
  generated: true
  caption: string
  hashtags: string[]
  images: string[]
}

export interface PlatformsContent {
  facebook?: FacebookPlatformContent
  instagram?: InstagramPlatformContent
}

export interface DraftContent {
  success: boolean
  error: string | null
  data: {
    status: string
    approval_status: string | null
    platforms: PlatformsContent
  }
}

export interface DraftResponse {
  thread_id: string
  status: DraftStatus
  approval_status: ApprovalStatus
  content: DraftContent
  _links: Record<string, LinkResponse>
}

export function isTerminalState(draft: DraftResponse): boolean {
  return draft.status === 'published' || draft.status === 'rejected'
}

// ─── Property payload ──────────────────────────────────────────────────────────

export interface PropertyLocation {
  city: string
  postalCode: string
  country: string
}

export interface LivingArea {
  surfaceArea: number
  roomsCount: number
  numberOfBedrooms: number
}

export interface PropertyEnvironment {
  hasPool: boolean
  numberOfParkings: number
}

export interface CoOwnership {
  fee: number
}

export interface PropertyAmenities {
  comfort: string[]
  security: string[]
  heatingSystem: string[]
  heatingPowerSupply: string[]
  heatingDistribution: string[]
  residence: boolean
  closedResidence: boolean
}

export interface PropertyPhoto {
  url: string
}

export interface PropertyJson {
  id: number
  uid: string
  property_type: string
  sub_type: string
  transaction_type: string
  location: PropertyLocation
  living_area: LivingArea
  mandate_price: number
  charges: number
  taxes: number
  description: string
  balcony_count: number
  terrace_count: number
  overall_condition: string
  work_required: boolean
  environment: PropertyEnvironment
  co_ownership: CoOwnership
  amenities: PropertyAmenities
  exposures: string[]
  is_prestige: boolean
  photos: PropertyPhoto[]
  created_at: string
}

export interface GenerateDraftRequest {
  input: string
  property_json: PropertyJson
}
