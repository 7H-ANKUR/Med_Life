import re
import os

filepath = r'C:\Users\ankur\Documents\projects\med\travel-health-finder\apps\web\src\app\profile\page.tsx'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update imports
imports = """'use client'

import React, { useState, useEffect } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { usersService, authService } from '@/services/api'
"""
content = re.sub(r"'use client'\s*import React, { useState } from 'react'\s*import Link from 'next/link'", imports, content)


# 2. Add Component State
state_logic = """export default function ProfilePage() {
  const router = useRouter()
  const [isSidebarOpen, setIsSidebarOpen] = useState(false)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [formData, setFormData] = useState({
    display_name: '',
    email: '',
    phone_number: '',
    default_city: ''
  })

  useEffect(() => {
    fetchProfile()
  }, [])

  const fetchProfile = async () => {
    try {
      const res = await usersService.getProfile()
      setFormData({
        display_name: res.data.display_name || '',
        email: res.data.email || '',
        phone_number: res.data.phone_number || '',
        default_city: res.data.default_city || ''
      })
    } catch (err) {
      console.error(err)
      router.push('/login')
    } finally {
      setLoading(false)
    }
  }

  const handleSave = async () => {
    setSaving(true)
    try {
      await usersService.updateProfile(formData)
      alert('Profile updated successfully!')
    } catch (err) {
      console.error(err)
      alert('Failed to update profile')
    } finally {
      setSaving(false)
    }
  }

  const handleLogout = async () => {
    try {
      const token = localStorage.getItem('refresh_token')
      if (token) {
        await authService.logout(token)
      }
    } catch (e) {
      console.error(e)
    } finally {
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      router.push('/login')
    }
  }

  if (loading) {
    return <div className="min-h-screen flex items-center justify-center text-on-surface">Loading profile...</div>
  }
"""

content = re.sub(r"export default function ProfilePage\(\) \{\s*const \[isSidebarOpen, setIsSidebarOpen\] = useState\(false\)", state_logic, content)

# 3. Replace Hardcoded Names / Roles
content = content.replace("Chief Surgeon", "Travel Health Finder User")
content = content.replace("Dr. Elena Sterling", "{formData.display_name || 'Anonymous User'}")
content = content.replace("Senior Cardiologist • license #8829-XJ", "Manage your personal information and preferences below.")

# 4. Replace Inputs
content = re.sub(
    r'<input [^>]*value="Elena Sterling"[^>]*>',
    r'<input className="w-full h-[56px] px-sm rounded-xl border border-outline-variant bg-surface-container-lowest focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none transition-all" type="text" value={formData.display_name} onChange={(e) => setFormData({...formData, display_name: e.target.value})} placeholder="Your full name" />',
    content
)

content = re.sub(
    r'<input [^>]*value="e\.sterling@medlife\.org"[^>]*>',
    r'<input className="w-full h-[56px] px-sm rounded-xl border border-outline-variant bg-surface-container-lowest focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none transition-all" type="email" value={formData.email} onChange={(e) => setFormData({...formData, email: e.target.value})} placeholder="Your email address" />',
    content
)

content = re.sub(
    r'<input [^>]*value="\+1 \(555\) 902-1244"[^>]*>',
    r'<input className="w-full h-[56px] px-sm rounded-xl border border-outline-variant bg-surface-container-lowest focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none transition-all" type="tel" value={formData.phone_number} onChange={(e) => setFormData({...formData, phone_number: e.target.value})} placeholder="Your phone number" />',
    content
)

# Use the "Medical ID" input as "Default City"
content = content.replace("Medical ID", "Default City")
content = re.sub(
    r'<input [^>]*value="MED-992-STER-0"[^>]*>',
    r'<input className="w-full h-[56px] px-sm rounded-xl border border-outline-variant bg-surface-container-lowest focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none transition-all" type="text" value={formData.default_city} onChange={(e) => setFormData({...formData, default_city: e.target.value})} placeholder="Your default city" />',
    content
)

# 5. Wire Save Changes
content = content.replace(
    '<button className="flex items-center gap-2 px-6 py-3 bg-primary text-white rounded-full font-label-lg text-label-lg shadow-lg hover:shadow-primary/25 transition-all">',
    '<button onClick={handleSave} disabled={saving} className="flex items-center gap-2 px-6 py-3 bg-primary text-white rounded-full font-label-lg text-label-lg shadow-lg hover:shadow-primary/25 transition-all disabled:opacity-50">'
)

# 6. Wire Logout
content = content.replace(
    '<a className="flex items-center gap-4 text-error px-4 py-3 hover:bg-error-container/20 transition-colors rounded-xl" href="#">\n<span className="material-symbols-outlined">logout</span>\n<span className="font-label-lg text-label-lg">Logout</span>\n</a>',
    '<button onClick={handleLogout} className="w-full flex items-center gap-4 text-error px-4 py-3 hover:bg-error-container/20 transition-colors rounded-xl">\n<span className="material-symbols-outlined">logout</span>\n<span className="font-label-lg text-label-lg">Logout</span>\n</button>'
)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print("Profile component refactored successfully.")
