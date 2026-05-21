import { z } from 'zod'

export const PropertyTypeEnum = z.enum(['apartment', 'house', 'land', 'commercial', 'parking'])
export const TransactionTypeEnum = z.enum(['sale', 'rental'])
export const OverallConditionEnum = z.enum(['excellent', 'good', 'fair', 'poor'])
export const ExposureEnum = z.enum(['north', 'south', 'east', 'west'])
export const PlatformEnum = z.enum(['facebook', 'instagram'])

export const COMFORT_OPTIONS = [
  'air-conditioning', 'double-glazing', 'electric-shutters', 'home-automation',
  'optical-fiber', 'intercom', 'video-intercom', 'fireplace', 'central-vacuum',
  'high-speed-internet', 'ev-charging-station', 'outdoor-lighting',
] as const

export const SECURITY_OPTIONS = [
  'digicode', 'alarm-system', 'security-door', 'concierge', 'caretaker',
  'video-surveillance', 'fenced-property', 'reinforced-door',
] as const

export const HEATING_SYSTEM_OPTIONS = ['individual', 'collective', 'underfloor', 'radiator'] as const
export const HEATING_POWER_OPTIONS = ['electricity', 'gas', 'heat-pump', 'oil', 'wood'] as const
export const HEATING_DISTRIBUTION_OPTIONS = ['individual-meter', 'collective-meter', 'smart-zoning'] as const

export const EXPOSURE_OPTIONS = ['north', 'south', 'east', 'west'] as const
export const PLATFORM_OPTIONS = ['facebook', 'instagram'] as const

export const propertyFormSchema = z.object({
  // Social media
  userPrompt: z.string().min(10, 'Le prompt doit contenir au moins 10 caractères'),
  platforms: z.array(PlatformEnum).min(1, 'Sélectionner au moins une plateforme'),

  // General
  description: z.string().min(1, 'Description requise'),
  property_type: PropertyTypeEnum,
  sub_type: z.string().min(1, 'Sous-type requis (ex: T4, Villa, Studio)'),
  transaction_type: TransactionTypeEnum,
  mandate_price: z.coerce.number().positive('Prix requis'),
  charges: z.coerce.number().min(0),
  taxes: z.coerce.number().min(0),
  is_prestige: z.boolean(),

  // Location
  city: z.string().min(1, 'Ville requise'),
  postalCode: z.string().min(1, 'Code postal requis'),
  country: z.string().min(1, 'Pays requis'),

  // Characteristics
  surfaceArea: z.coerce.number().positive('Surface requise'),
  roomsCount: z.coerce.number().int().positive('Nombre de pièces requis'),
  numberOfBedrooms: z.coerce.number().int().min(0),
  overall_condition: OverallConditionEnum,
  work_required: z.boolean(),
  exposures: z.array(ExposureEnum).min(1, 'Au moins une exposition requise'),

  // Exteriors
  balcony_count: z.coerce.number().int().min(0),
  terrace_count: z.coerce.number().int().min(0),
  numberOfParkings: z.coerce.number().int().min(0),

  // Photos
  photos: z.array(z.string().url('URL invalide')),

  // Amenities
  comfort: z.array(z.string()),
  security: z.array(z.string()),
  heatingSystem: z.array(z.string()),
  heatingPowerSupply: z.array(z.string()),
  heatingDistribution: z.array(z.string()),
  residence: z.boolean(),
  closedResidence: z.boolean(),
})

export type PropertyFormValues = z.infer<typeof propertyFormSchema>
