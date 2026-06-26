import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { AuthProvider } from '@/store/AuthContext'
import { LocationProvider } from '@/store/LocationContext'
import { SearchProvider } from '@/store/SearchContext'
import { EmergencyProvider } from '@/store/EmergencyContext'

const inter = Inter({ subsets: ['latin'], variable: '--font-inter' })

export const metadata: Metadata = {
  title: 'MedLife — Precision Clinical Search',
  description: 'Find nearby doctors, hospitals, and clinics. AI-powered symptom analysis and emergency-aware medical search.',
  keywords: 'find doctor, nearby hospital, travel health, medical finder, emergency doctor',
  openGraph: {
    title: 'MedLife — Precision Clinical Search',
    description: 'Find the right doctor, right now.',
    type: 'website',
  },
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={inter.variable}>
      <head>
        <link
          rel="stylesheet"
          href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200&display=swap"
        />
      </head>
      <body>
        <AuthProvider>
          <LocationProvider>
            <SearchProvider>
              <EmergencyProvider>
                {children}
              </EmergencyProvider>
            </SearchProvider>
          </LocationProvider>
        </AuthProvider>
      </body>
    </html>
  )
}
