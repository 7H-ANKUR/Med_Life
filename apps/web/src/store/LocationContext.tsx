'use client'
import { createContext, useContext, useState, useEffect, ReactNode } from 'react'

interface Location { lat: number; lng: number }

interface LocationContextType {
  location: Location | null
  city: string
  permissionDenied: boolean
  detecting: boolean
  setCity: (city: string) => void
  setLocation: (loc: Location) => void
  requestGPS: () => void
}

const LocationContext = createContext<LocationContextType | null>(null)

export function LocationProvider({ children }: { children: ReactNode }) {
  const [location, setLocation] = useState<Location | null>(null)
  const [city, setCity] = useState('')
  const [permissionDenied, setPermissionDenied] = useState(false)
  const [detecting, setDetecting] = useState(true)

  // Auto-detect city + coords via ipapi.co on first load
  useEffect(() => {
    const detect = async () => {
      try {
        const res = await fetch('https://ipapi.co/json/')
        if (res.ok) {
          const data = await res.json()
          if (data?.city) setCity(data.city)
          if (data?.latitude && data?.longitude) {
            setLocation({ lat: data.latitude, lng: data.longitude })
          }
        }
      } catch {
        // Silently fail — user can still pick city manually
      } finally {
        setDetecting(false)
      }
    }
    detect()
  }, [])

  const requestGPS = () => {
    if (!navigator.geolocation) {
      setPermissionDenied(true)
      return
    }
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        setLocation({ lat: pos.coords.latitude, lng: pos.coords.longitude })
        setPermissionDenied(false)
      },
      () => setPermissionDenied(true),
      { timeout: 8000 }
    )
  }

  return (
    <LocationContext.Provider value={{ location, city, permissionDenied, detecting, setCity, setLocation, requestGPS }}>
      {children}
    </LocationContext.Provider>
  )
}

export const useLocation = () => {
  const ctx = useContext(LocationContext)
  if (!ctx) throw new Error('useLocation must be inside LocationProvider')
  return ctx
}
