'use client'
import { useEffect, useState } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { historyService } from '@/services/api'
import { useSearch } from '@/store/SearchContext'
import { useLocation } from '@/store/LocationContext'

const URGENCY_COLOR: Record<string, string> = {
  emergency: '#DC2626', high: '#D97706', moderate: '#2563EB', low: '#16A34A'
}

export default function HistoryPage() {
  const router = useRouter()
  const { setLastSymptomText } = useSearch()
  const { city } = useLocation()
  const [history, setHistory] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    historyService.list().then(res => { setHistory(res.data.history || res.data || []); setLoading(false) }).catch(() => setLoading(false))
  }, [])

  const handleRerun = (item: any) => {
    setLastSymptomText(item.symptom_text)
    router.push('/search')
  }

  const handleDelete = async (id: string) => {
    await historyService.deleteItem(id)
    setHistory(prev => prev.filter(h => h.id !== id))
  }

  return (
    <div className="page-container">
      <div className="header">
        <span style={{ fontWeight: 700, fontSize: 17 }}>🕐 Search History</span>
        <div style={{ flex: 1 }} />
        {history.length > 0 && (
          <button onClick={async () => { await historyService.clearAll(); setHistory([]) }} style={{ background: 'none', border: 'none', color: 'var(--emergency)', cursor: 'pointer', fontSize: 13, fontWeight: 600 }}>
            Clear All
          </button>
        )}
      </div>

      <div style={{ padding: '16px 16px 100px' }}>
        {loading ? (
          Array(4).fill(0).map((_, i) => <div key={i} className="skeleton" style={{ height: 90, marginBottom: 12 }} />)
        ) : history.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '60px 24px', color: 'var(--muted)' }}>
            <div style={{ fontSize: 52, marginBottom: 12 }}>🕐</div>
            <div style={{ fontWeight: 700, fontSize: 16, color: 'var(--text)', marginBottom: 8 }}>No history yet</div>
            <Link href="/search" className="btn btn-primary" style={{ display: 'block', textDecoration: 'none', maxWidth: 200, margin: '16px auto 0' }}>Search Now</Link>
          </div>
        ) : (
          history.map(item => (
            <div key={item.id} className="card card-hover" style={{ marginBottom: 12, cursor: 'pointer' }} onClick={() => handleRerun(item)}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 8 }}>
                <div style={{ flex: 1 }}>
                  <div style={{ fontWeight: 600, fontSize: 14, color: 'var(--text)', marginBottom: 4, lineClamp: 2 }}>{item.symptom_text}</div>
                  <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
                    {item.specialist_type && <span className="badge badge-hospital">{item.specialist_type}</span>}
                    {item.urgency_level && <span className="badge" style={{ background: `${URGENCY_COLOR[item.urgency_level]}22`, color: URGENCY_COLOR[item.urgency_level] }}>{item.urgency_level}</span>}
                    {item.city && <span style={{ fontSize: 11, color: 'var(--muted)' }}>📍 {item.city}</span>}
                  </div>
                </div>
                <button onClick={(e) => { e.stopPropagation(); handleDelete(item.id) }} style={{ background: 'none', border: 'none', color: 'var(--muted)', cursor: 'pointer', fontSize: 16, padding: 4 }}>✕</button>
              </div>
              <div style={{ fontSize: 11, color: 'var(--muted)' }}>
                {new Date(item.created_at).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' })}
                {item.result_count != null && ` · ${item.result_count} results`}
              </div>
            </div>
          ))
        )}
      </div>

      <nav className="bottom-nav">
        <Link href="/search" className="bottom-nav-item"><svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>Search</Link>
        <Link href="/saved" className="bottom-nav-item"><svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="m19 21-7-4-7 4V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"/></svg>Saved</Link>
        <Link href="/history" className="bottom-nav-item active"><svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>History</Link>
        <Link href="/profile" className="bottom-nav-item"><svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>Profile</Link>
      </nav>
    </div>
  )
}
