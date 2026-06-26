'use client'
import { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { authService } from '@/services/api'

interface User {
  id: string
  email: string
  display_name?: string
  default_city?: string
  language_pref: string
}

interface AuthContextType {
  user: User | null
  isLoading: boolean
  isAuthenticated: boolean
  login: (email: string, password: string) => Promise<void>
  signup: (email: string, password: string, name?: string) => Promise<void>
  logout: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    // Restore session from localStorage
    const token = localStorage.getItem('access_token')
    const savedUser = localStorage.getItem('user')
    if (token && savedUser) {
      try { setUser(JSON.parse(savedUser)) } catch { /* ignore */ }
    }
    setIsLoading(false)
  }, [])

  const login = async (email: string, password: string) => {
    const res = await authService.login(email, password)
    localStorage.setItem('access_token', res.data.access_token)
    localStorage.setItem('refresh_token', res.data.refresh_token)
    // Decode user from token payload (base64)
    const payload = JSON.parse(atob(res.data.access_token.split('.')[1]))
    const userData: User = { id: payload.sub, email, language_pref: 'en' }
    setUser(userData)
    localStorage.setItem('user', JSON.stringify(userData))
  }

  const signup = async (email: string, password: string, name?: string) => {
    const res = await authService.signup(email, password, name)
    localStorage.setItem('access_token', res.data.access_token)
    localStorage.setItem('refresh_token', res.data.refresh_token)
    const userData: User = { id: '', email, display_name: name, language_pref: 'en' }
    setUser(userData)
    localStorage.setItem('user', JSON.stringify(userData))
  }

  const logout = async () => {
    const refreshToken = localStorage.getItem('refresh_token') || ''
    try { await authService.logout(refreshToken) } catch { /* ignore */ }
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user')
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ user, isLoading, isAuthenticated: !!user, login, signup, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be inside AuthProvider')
  return ctx
}
