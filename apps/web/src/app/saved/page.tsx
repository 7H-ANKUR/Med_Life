'use client'
import { useEffect, useState } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { savedService } from '@/services/api'

export default function SavedPage() {
  const router = useRouter()
  const [saved, setSaved] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState('All')

  useEffect(() => {
    savedService.list()
      .then(res => { setSaved(res.data.saved || res.data || []); setLoading(false) })
      .catch(() => { setLoading(false) })
  }, [])

  const handleRemove = async (id: string) => {
    await savedService.remove(id)
    setSaved(prev => prev.filter(s => s.id !== id))
  }

  const filters = ['All', 'Hospital', 'Clinic', 'Pharmacy']
  const filtered = filter === 'All' ? saved : saved.filter(s => s.place_type === filter.toLowerCase())

  return (
    <div className="page-container">
      <div className="header">
        <span style={{ fontWeight: 700, fontSize: 17 }}>🔖 Saved Places</span>
      </div>

      <div style={{ padding: '16px 16px 100px' }}>
        {/* Filter tabs */}
        <div className="filter-bar" style={{ marginBottom: 16 }}>
          {filters.map(f => (
            <button key={f} className={`btn-pill ${filter === f ? 'btn-pill-active' : ''}`} onClick={() => setFilter(f)} style={{ flexShrink: 0 }}>{f}</button>
          ))}
        </div>

        {loading ? (
          Array(3).fill(0).map((_, i) => <div key={i} className="skeleton" style={{ height: 100, marginBottom: 12 }} />)
        ) : filtered.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '60px 24px', color: 'var(--muted)' }}>
            <div style={{ fontSize: 52, marginBottom: 12 }}>🔖</div>
            <div style={{ fontWeight: 700, fontSize: 16, color: 'var(--text)', marginBottom: 8 }}>No saved places yet</div>
            <p style={{ fontSize: 14 }}>Search for a doctor or hospital and save it here for quick access.</p>
            <Link href="/search" className="btn btn-primary" style={{ display: 'block', textDecoration: 'none', maxWidth: 200, margin: '16px auto 0' }}>
              Find a Doctor
            </Link>
          </div>
        ) : (
          filtered.map(place => (
            <div key={place.id} className="result-card" style={{ marginBottom: 12 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div style={{ flex: 1 }}>
                  <div style={{ fontWeight: 700, fontSize: 15, marginBottom: 4, color: 'var(--text)' }}>{place.place_name}</div>
                  <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
                    {place.place_type && <span className={`badge badge-${place.place_type}`}>{place.place_type}</span>}
                    {place.city && <span style={{ fontSize: 12, color: 'var(--muted)' }}>📍 {place.city}</span>}
                    {place.rating && <span style={{ fontSize: 12, color: 'var(--muted)' }}>⭐ {place.rating}</span>}
                  </div>
                </div>
                <button onClick={() => handleRemove(place.id)} style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--muted)', fontSize: 18, padding: 4 }}>✕</button>
              </div>
              <div style={{ display: 'flex', gap: 8, marginTop: 12 }}>
                <button
                  onClick={() => window.open(`https://www.google.com/maps/dir/?api=1&destination=${place.latitude},${place.longitude}&travelmode=driving`, '_blank')}
                  className="btn btn-primary"
                  style={{ height: 38, fontSize: 13, flex: 1 }}
                >
                  🗺️ Navigate
                </button>
                <button onClick={() => router.push(`/place/${place.doctor_id || place.google_place_id}`)} className="btn btn-secondary" style={{ height: 38, fontSize: 13, padding: '0 14px' }}>
                  Details
                </button>
              </div>
            </div>
          ))
        )}
      </div>

      <nav className="bottom-nav">
        <Link href="/search" className="bottom-nav-item"><svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>Search</Link>
        <Link href="/saved" className="bottom-nav-item active"><svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="m19 21-7-4-7 4V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"/></svg>Saved</Link>
        <Link href="/history" className="bottom-nav-item"><svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>History</Link>
        <Link href="/profile" className="bottom-nav-item"><svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>Profile</Link>
      </nav>
    </div>
  )
}
