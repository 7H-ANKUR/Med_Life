'use client'
import { createContext, useContext, useState, ReactNode } from 'react'

interface EmergencyContextType {
  isEmergency: boolean
  setEmergency: (val: boolean) => void
}

const EmergencyContext = createContext<EmergencyContextType | null>(null)

export function EmergencyProvider({ children }: { children: ReactNode }) {
  const [isEmergency, setEmergency] = useState(false)
  return (
    <EmergencyContext.Provider value={{ isEmergency, setEmergency }}>
      {children}
    </EmergencyContext.Provider>
  )
}

export const useEmergency = () => {
  const ctx = useContext(EmergencyContext)
  if (!ctx) throw new Error('useEmergency must be inside EmergencyProvider')
  return ctx
}
