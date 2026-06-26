'use client'
import { createContext, useContext, useState, ReactNode } from 'react'

export interface AnalysisResult {
  specialist_type: string
  specialist_explanation: string
  urgency_level: 'low' | 'moderate' | 'high' | 'emergency'
  urgency_reason: string
  emergency_mode: boolean
  fee_estimate?: { min: number; max: number; currency: string; note: string }
  search_id?: string
  fallback?: boolean
}

interface SearchContextType {
  analysisResult: AnalysisResult | null
  setAnalysisResult: (result: AnalysisResult | null) => void
  lastSymptomText: string
  setLastSymptomText: (text: string) => void
}

const SearchContext = createContext<SearchContextType | null>(null)

export function SearchProvider({ children }: { children: ReactNode }) {
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null)
  const [lastSymptomText, setLastSymptomText] = useState('')

  return (
    <SearchContext.Provider value={{ analysisResult, setAnalysisResult, lastSymptomText, setLastSymptomText }}>
      {children}
    </SearchContext.Provider>
  )
}

export const useSearch = () => {
  const ctx = useContext(SearchContext)
  if (!ctx) throw new Error('useSearch must be inside SearchProvider')
  return ctx
}
