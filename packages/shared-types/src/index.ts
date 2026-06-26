// Shared TypeScript types for Travel Health Finder
// Used by both apps/web and any future packages

export type UrgencyLevel = 'low' | 'moderate' | 'high' | 'emergency'

export type PlaceType = 'hospital' | 'clinic' | 'pharmacy'

export interface LocationPoint {
  lat: number
  lng: number
}

export interface FeeRange {
  min: number
  max: number
  currency: string
  note?: string
}

export interface PlaceResult {
  place_id: string
  name: string
  place_type: PlaceType
  address?: string
  phone?: string
  rating?: number
  review_count?: number
  open_now: boolean
  distance_meters?: number
  distance_label?: string
  fee_estimate?: FeeRange
  specialist_types: string[]
  score?: number
  emergency_capable: boolean
  location?: LocationPoint
  maps_url?: string
  photo_url?: string
}

export interface AnalysisResult {
  specialist_type: string
  specialist_explanation: string
  urgency_level: UrgencyLevel
  urgency_reason: string
  emergency_mode: boolean
  fee_estimate?: FeeRange
  search_id?: string
  fallback?: boolean
}

export interface NearbySearchParams {
  lat?: number
  lng?: number
  city?: string
  specialist_type?: string
  place_type?: PlaceType | 'all'
  emergency?: boolean
  open_now?: boolean
  budget_max?: number
  radius?: number
  rating_min?: number
  language?: string
  limit?: number
}

export interface User {
  id: string
  email: string
  display_name?: string
  default_city?: string
  language_pref: string
}

export interface SavedPlace {
  id: string
  google_place_id: string
  place_name?: string
  place_type?: PlaceType
  city?: string
  rating?: number
  specialist_type?: string
  notes?: string
  saved_at: string
}

export interface SearchHistory {
  id: string
  symptom_text: string
  specialist_type?: string
  urgency_level?: UrgencyLevel
  city?: string
  result_count?: number
  emergency_mode: boolean
  created_at: string
}
