'use client'
import { useEffect, useState } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { placesService, savedService, feedbackService } from '@/services/api'

export default function PlaceDetailPage() {
  const params = useParams()
  const router = useRouter()
  const placeId = params.placeId as string

  const [place, setPlace] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [saved, setSaved] = useState(false)
  const [feedback, setFeedback] = useState<1 | -1 | null>(null)
  const [feedbackSubmitted, setFeedbackSubmitted] = useState(false)

  useEffect(() => {
    placesService.detail(placeId).then(res => { setPlace(res.data); setLoading(false) }).catch(() => setLoading(false))
  }, [placeId])

  const navigate = () => {
    if (place?.location) {
      window.open(`https://www.google.com/maps/dir/?api=1&destination=${place.location.lat},${place.location.lng}&travelmode=driving`, '_blank')
    }
  }

  const handleSave = async () => {
    try {
      if (!saved) await savedService.save({ google_place_id: placeId, place_name: place?.name, place_type: 'hospital' })
      setSaved(!saved)
    } catch { }
  }

  const handleFeedback = async (rating: 1 | -1) => {
    try {
      await feedbackService.submit({ google_place_id: placeId, rating })
      setFeedback(rating)
      setFeedbackSubmitted(true)
    } catch { }
  }

  if (loading) {
    return (
      <div className="page-container" style={{ padding: 16 }}>
        <div className="skeleton" style={{ height: 409, borderRadius: 12, marginBottom: -40 }} />
        <div className="skeleton" style={{ height: 200, borderRadius: 12, position: 'relative', zIndex: 10 }} />
      </div>
    )
  }

  if (!place) {
    return (
      <div className="page-container" style={{ padding: 24, textAlign: 'center', paddingTop: 100 }}>
        <span className="material-symbols-outlined" style={{ fontSize: 64, color: '#c3c6d7', marginBottom: 16 }}>location_off</span>
        <p style={{ color: '#434655', marginBottom: 24 }}>Place not found or unavailable.</p>
        <button className="btn btn-primary" onClick={() => router.back()}>Go Back</button>
      </div>
    )
  }

  const bgImage = place.photos?.[0] || 'https://images.unsplash.com/photo-1519494026892-80bbd2d6fd0d?w=800'
  const isSunday = new Date().getDay() === 0

  return (
    <div style={{ minHeight: '100dvh', background: '#f8f9fa', fontFamily: 'Inter, system-ui, sans-serif' }}>
      
      {/* ── Header ── */}
      <div style={{
        position: 'fixed', top: 0, left: 0, right: 0, zIndex: 50,
        background: 'rgba(248, 249, 250, 0.85)', backdropFilter: 'blur(12px)',
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        padding: '0 16px', height: 60, borderBottom: '1px solid rgba(195,198,215,0.30)',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <button onClick={() => router.back()} style={{
            width: 40, height: 40, borderRadius: '50%', background: 'white',
            border: '1px solid #e5e7eb', display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer',
            boxShadow: '0 2px 8px rgba(0,0,0,0.05)',
          }}>
            <span className="material-symbols-outlined" style={{ color: '#191c1d', fontSize: 20 }}>arrow_back</span>
          </button>
          <span style={{ fontWeight: 700, fontSize: 16, color: '#191c1d' }}>Place Details</span>
        </div>
        <div style={{ display: 'flex', gap: 8 }}>
          <button style={{ width: 40, height: 40, borderRadius: '50%', background: 'white', border: '1px solid #e5e7eb', display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer' }}>
            <span className="material-symbols-outlined" style={{ color: '#191c1d', fontSize: 20 }}>share</span>
          </button>
          <button onClick={handleSave} style={{ width: 40, height: 40, borderRadius: '50%', background: 'white', border: '1px solid #e5e7eb', display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer' }}>
            <span className={saved ? "material-symbols-outlined mat-fill" : "material-symbols-outlined"} style={{ color: saved ? '#004ac6' : '#191c1d', fontSize: 20 }}>bookmark</span>
          </button>
        </div>
      </div>

      {/* ── Hero Photo ── */}
      <div style={{ position: 'relative', height: 409, width: '100%' }}>
        <div style={{ position: 'absolute', inset: 0, backgroundImage: `url(${bgImage})`, backgroundSize: 'cover', backgroundPosition: 'center' }} />
        <div style={{ position: 'absolute', inset: 0, background: 'linear-gradient(to top, rgba(0,0,0,0.6) 0%, transparent 40%)' }} />
      </div>

      {/* ── Content ── */}
      <div style={{ position: 'relative', zIndex: 10, marginTop: -40, padding: '0 16px 40px', maxWidth: 600, margin: '-40px auto 0' }}>
        
        {/* Main floating card */}
        <div style={{ background: 'white', borderRadius: 16, padding: 24, boxShadow: '0 4px 20px rgba(0,0,0,0.08)', marginBottom: 20 }}>
          <h2 style={{ fontSize: 24, fontWeight: 700, color: '#191c1d', margin: '0 0 8px', lineHeight: 1.2 }}>
            {place.name}
          </h2>
          <div style={{ display: 'flex', alignItems: 'center', gap: 6, color: '#004ac6', fontWeight: 600, fontSize: 15, marginBottom: 16 }}>
            <span className="material-symbols-outlined" style={{ fontSize: 20 }}>stethoscope</span>
            {place.speciality?.split(',')[0]?.trim() || place.place_type}
          </div>
          
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 12, marginBottom: 20 }}>
            {place.rating && (
              <div style={{ display: 'flex', alignItems: 'center', gap: 4, background: '#f3f4f5', padding: '6px 12px', borderRadius: 8 }}>
                <span className="material-symbols-outlined mat-fill" style={{ color: '#F59E0B', fontSize: 18 }}>star</span>
                <span style={{ fontWeight: 700, fontSize: 14 }}>{place.rating}</span>
                <span style={{ color: '#6B7280', fontSize: 14 }}>({place.review_count?.toLocaleString() || '1k+'})</span>
              </div>
            )}
            <div style={{ display: 'flex', alignItems: 'center', gap: 6, background: place.open_now ? 'rgba(20,184,166,0.1)' : '#FEF2F2', padding: '6px 12px', borderRadius: 8 }}>
              <span style={{ width: 8, height: 8, borderRadius: '50%', background: place.open_now ? '#14B8A6' : '#DC2626' }} />
              <span style={{ color: place.open_now ? '#14B8A6' : '#DC2626', fontWeight: 600, fontSize: 14 }}>
                {place.open_now ? 'OPEN NOW' : 'CLOSED'}
              </span>
            </div>
          </div>

          <div style={{ display: 'flex', alignItems: 'flex-start', gap: 12, color: '#434655', fontSize: 14, lineHeight: 1.6 }}>
            <span className="material-symbols-outlined" style={{ fontSize: 20, color: '#6B7280', marginTop: 2 }}>location_on</span>
            <span>{place.address}</span>
          </div>
        </div>

        {/* Teal Call Banner */}
        {place.phone && place.phone !== 'Contact Clinic directly' && (
          <div style={{ background: '#14B8A6', borderRadius: 16, padding: '20px 24px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 20, cursor: 'pointer', boxShadow: '0 4px 14px rgba(20,184,166,0.3)' }} onClick={() => window.open(`tel:${place.phone}`)}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
              <div style={{ width: 48, height: 48, borderRadius: '50%', background: 'rgba(255,255,255,0.2)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <span className="material-symbols-outlined" style={{ color: 'white', fontSize: 24 }}>call</span>
              </div>
              <div>
                <div style={{ color: 'rgba(255,255,255,0.9)', fontSize: 12, fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 2 }}>Primary Contact</div>
                <div style={{ color: 'white', fontSize: 20, fontWeight: 700 }}>{place.phone}</div>
              </div>
            </div>
            <span className="material-symbols-outlined" style={{ color: 'white' }}>chevron_right</span>
          </div>
        )}

        {/* Action Buttons */}
        <div style={{ display: 'flex', gap: 12, marginBottom: 32 }}>
          <button id={`navigate-detail-${placeId}`} onClick={navigate} style={{
            flex: 1, background: '#004ac6', color: 'white', border: 'none', borderRadius: 999,
            padding: 16, fontWeight: 600, fontSize: 16, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8, cursor: 'pointer',
            boxShadow: '0 4px 14px rgba(0,74,198,0.2)'
          }}>
            <span className="material-symbols-outlined">directions</span> Navigate
          </button>
          {place.phone && (
            <a href={`tel:${place.phone}`} style={{
              flex: 1, background: 'transparent', color: '#14B8A6', border: '2px solid #14B8A6', borderRadius: 999,
              padding: 14, fontWeight: 600, fontSize: 16, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8, textDecoration: 'none',
            }}>
              <span className="material-symbols-outlined">call</span> Call
            </a>
          )}
        </div>

        {/* Hours Card */}
        {place.hours?.length > 0 && (
          <div style={{ background: 'white', borderRadius: 16, padding: 24, boxShadow: '0 1px 6px rgba(0,0,0,0.04)', marginBottom: 24, border: '1px solid #e5e7eb' }}>
            <h3 style={{ fontSize: 18, fontWeight: 700, color: '#191c1d', display: 'flex', alignItems: 'center', gap: 8, margin: '0 0 16px' }}>
              <span className="material-symbols-outlined" style={{ color: '#004ac6' }}>schedule</span>
              Opening Hours
            </h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
              {place.hours.map((h: string, i: number) => {
                const isSun = h.toLowerCase().includes('sunday')
                return (
                  <div key={i} style={{ display: 'flex', justifyContent: 'space-between', fontSize: 15, paddingBottom: 12, borderBottom: i === place.hours.length - 1 ? 'none' : '1px solid #f3f4f5' }}>
                    <span style={{ color: isSun ? '#DC2626' : '#191c1d', fontWeight: 500 }}>{h.split(':')[0]}</span>
                    <span style={{ color: isSun ? '#DC2626' : '#6B7280', fontWeight: isSun ? 600 : 400 }}>{h.substring(h.indexOf(':') + 1).trim() || 'Closed'}</span>
                  </div>
                )
              })}
            </div>
          </div>
        )}

        {/* Reviews */}
        {place.reviews?.length > 0 && (
          <div style={{ marginBottom: 32 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
              <h3 style={{ fontSize: 18, fontWeight: 700, color: '#191c1d', margin: 0 }}>Recent Reviews</h3>
              <button style={{ background: 'none', border: 'none', color: '#004ac6', fontWeight: 600, fontSize: 14, cursor: 'pointer' }}>See All</button>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
              {place.reviews.slice(0, 3).map((r: any, i: number) => (
                <div key={i} style={{ background: 'white', padding: 20, borderRadius: 16, border: '1px solid #e5e7eb' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 12 }}>
                    <div style={{ width: 40, height: 40, borderRadius: '50%', background: '#004ac6', color: 'white', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 700 }}>
                      {r.author_name?.charAt(0) || 'U'}
                    </div>
                    <div>
                      <div style={{ fontWeight: 600, fontSize: 15, color: '#191c1d' }}>{r.author_name}</div>
                      <div style={{ display: 'flex', color: '#F59E0B', fontSize: 12, marginTop: 2 }}>
                        {[...Array(5)].map((_, j) => (
                          <span key={j} className={j < (r.rating || 0) ? "material-symbols-outlined mat-fill" : "material-symbols-outlined"} style={{ fontSize: 14 }}>star</span>
                        ))}
                      </div>
                    </div>
                  </div>
                  <p style={{ fontSize: 14, color: '#434655', lineHeight: 1.6, margin: 0 }}>
                    "{r.text}"
                  </p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Feedback */}
        <div style={{ background: 'white', borderRadius: 16, padding: 24, textAlign: 'center', border: '1px solid #e5e7eb' }}>
          <h3 style={{ fontSize: 16, fontWeight: 700, color: '#191c1d', margin: '0 0 16px' }}>Did you find this helpful?</h3>
          {feedbackSubmitted ? (
            <div style={{ color: '#16A34A', fontWeight: 600, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8 }}>
              <span className="material-symbols-outlined mat-fill">check_circle</span>
              Thanks for your feedback!
            </div>
          ) : (
            <div style={{ display: 'flex', gap: 12, justifyContent: 'center' }}>
              <button onClick={() => handleFeedback(1)} style={{ flex: 1, padding: '12px', background: '#F0FDF4', border: '1.5px solid #86EFAC', borderRadius: 12, color: '#16A34A', fontWeight: 600, fontSize: 15, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8, cursor: 'pointer' }}>
                <span className="material-symbols-outlined mat-fill">thumb_up</span> Yes
              </button>
              <button onClick={() => handleFeedback(-1)} style={{ flex: 1, padding: '12px', background: '#FFF1F2', border: '1.5px solid #FECDD3', borderRadius: 12, color: '#DC2626', fontWeight: 600, fontSize: 15, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8, cursor: 'pointer' }}>
                <span className="material-symbols-outlined mat-fill">thumb_down</span> No
              </button>
            </div>
          )}
        </div>

      </div>
    </div>
  )
}
