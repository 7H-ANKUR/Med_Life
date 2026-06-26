"use client";

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { placesService } from '@/services/api';
import axios from 'axios';

const URGENCY_COLOR: Record<string, string> = {
  emergency: 'text-red-600 bg-red-50 border-red-200',
  high: 'text-orange-600 bg-orange-50 border-orange-200',
  moderate: 'text-amber-600 bg-amber-50 border-amber-200',
  low: 'text-green-600 bg-green-50 border-green-200',
};

function ProviderCard({ p, onClick }: { p: any, onClick?: () => void }) {
  const [phone, setPhone] = useState<string | null>(p.phone || null);
  const [imgLoaded, setImgLoaded] = useState(false);
  const [imgError, setImgError] = useState(false);

  // Fetch phone number from detail endpoint if not already present
  useEffect(() => {
    if (p.phone) return;
    let mounted = true;
    if (p.place_id) {
      placesService.detail(p.place_id).then(res => {
        if (mounted && res.data?.phone) {
          setPhone(res.data.phone);
        }
      }).catch(() => {});
    }
    return () => { mounted = false; };
  }, [p.place_id, p.phone]);

  // photo_url comes from backend's Apify batch fetch on /nearby
  const photoUrl = p.photo_url && !imgError ? p.photo_url : null;

  const initials = (p.name || 'Dr')
    .split(' ')
    .slice(0, 2)
    .map((n: string) => n[0])
    .join('')
    .toUpperCase();

  return (
    <div 
      className={`glass glass-edge p-6 rounded-3xl flex flex-col md:flex-row gap-5 group hover:shadow-[0_20px_40px_rgba(43,76,190,0.10)] transition-all ${onClick ? 'cursor-pointer' : ''}`}
      onClick={() => onClick && onClick()}
    >
      {/* Doctor/Clinic Image */}
      <div className="w-full md:w-44 h-44 rounded-2xl overflow-hidden shrink-0 relative bg-primary/10 flex items-center justify-center">
        {photoUrl ? (
          <div className="absolute inset-0 bg-cover bg-center" style={{ backgroundImage: `url(${photoUrl})` }} />
        ) : (
          <div className="flex flex-col items-center justify-center gap-2 text-primary">
            <span className="material-symbols-outlined text-5xl">local_hospital</span>
            <span className="text-2xl font-bold">{initials}</span>
          </div>
        )}
      </div>

      {/* Details */}
      <div className="flex-1 flex flex-col justify-between">
        <div>
          <div className="flex justify-between items-start mb-2 gap-4">
            <div>
              <h3 className="font-headline-md text-headline-md text-on-background group-hover:text-primary transition-colors">
                {p.name}
              </h3>
              <p className="text-tertiary font-label-lg text-label-lg mt-0.5">
                {p.speciality || p.place_type}
              </p>
            </div>
            {p.rating && (
              <div className="flex items-center gap-1 bg-amber-50 border border-amber-200 px-3 py-1 rounded-xl shrink-0">
                <span className="material-symbols-outlined text-amber-500 text-base">star</span>
                <span className="font-bold text-amber-700 text-sm">{p.rating}</span>
                {p.review_count && (
                  <span className="text-amber-500 text-xs">({p.review_count})</span>
                )}
              </div>
            )}
          </div>

          {/* Address */}
          <div className="flex items-start gap-2 mb-3">
            <span className="material-symbols-outlined text-on-surface-variant text-[16px] mt-0.5">location_on</span>
            <p className="text-body-sm text-on-surface-variant">{p.address}</p>
          </div>

          {/* Phone */}
          {phone && phone !== 'Contact Clinic directly' && (
            <a href={`tel:${phone}`} className="flex items-center gap-2 text-primary hover:underline text-label-sm mb-3">
              <span className="material-symbols-outlined text-[16px]">call</span>
              {phone}
            </a>
          )}

          {/* Tags */}
          <div className="flex flex-wrap gap-2 mt-1">
            {p.distance_label && (
              <span className="px-3 py-1 bg-primary/8 text-primary rounded-full text-label-sm font-label-lg flex items-center gap-1">
                <span className="material-symbols-outlined text-[14px]">near_me</span>
                {p.distance_label}
              </span>
            )}
            {p.fee_estimate && (
              <span className="px-3 py-1 bg-surface-container rounded-full text-label-sm text-on-surface-variant">
                ₹{p.fee_estimate.min}–₹{p.fee_estimate.max}
              </span>
            )}
            {p.place_type === 'hospital' && (
              <span className="px-3 py-1 bg-green-50 text-green-700 border border-green-200 rounded-full text-label-sm">
                Hospital
              </span>
            )}
          </div>
        </div>

        <div className="mt-5 flex flex-wrap gap-3">
          <button
            onClick={(e) => { e.stopPropagation(); if (p.maps_url) window.open(p.maps_url, '_blank'); }}
            className="px-6 py-2.5 bg-primary text-white rounded-full font-label-lg text-label-lg hover:shadow-lg hover:shadow-primary/30 transition-all active:scale-95 flex items-center gap-2"
          >
            <span className="material-symbols-outlined text-sm">map</span>
            View on Map
          </button>
          {phone && phone !== 'Contact Clinic directly' && (
            <a
              href={`tel:${phone}`}
              onClick={(e) => e.stopPropagation()}
              className="px-6 py-2.5 glass border border-primary/20 text-primary rounded-full font-label-lg text-label-lg hover:bg-primary/5 transition-all active:scale-95 flex items-center gap-2"
            >
              <span className="material-symbols-outlined text-sm">call</span>
              Call Now
            </a>
          )}
        </div>
      </div>
    </div>
  );
}

export default function ResultsPage() {
  const [analysis, setAnalysis] = useState<any>(null);
  const [providers, setProviders] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [selectedProvider, setSelectedProvider] = useState<any>(null);
  const [modalData, setModalData] = useState<any>(null);
  const [isModalLoading, setIsModalLoading] = useState(false);
  const router = useRouter();

  // Fetch full details when a provider is selected
  useEffect(() => {
    if (!selectedProvider) {
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setModalData(null);
      return;
    }
    let mounted = true;
    setIsModalLoading(true);
    placesService.detail(selectedProvider.place_id).then(res => {
      if (mounted) {
        setModalData(res.data);
        setIsModalLoading(false);
      }
    }).catch(err => {
      console.error(err);
      if (mounted) setIsModalLoading(false);
    });
    return () => { mounted = false; };
  }, [selectedProvider]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const stored = localStorage.getItem('lastAnalysis');
        if (!stored) {
          router.push('/search');
          return;
        }
        const parsed = JSON.parse(stored);
        setAnalysis(parsed);

        const specialist = parsed.specialists && parsed.specialists.length > 0
          ? parsed.specialists[0]
          : (parsed.specialist_type || undefined);

        // Fetch location (either from user's explicit pin or fallback to IP)
        let lat: number | undefined, lng: number | undefined, city: string | undefined;
        
        const storedLocation = localStorage.getItem('userLocation');
        if (storedLocation) {
          try {
            const loc = JSON.parse(storedLocation);
            lat = loc.lat;
            lng = loc.lng;
            console.log("Using exact user location from pin:", lat, lng);
          } catch (e) {
            console.error("Failed to parse userLocation", e);
          }
        }

        if (!lat || !lng) {
          try {
            const ipRes = await axios.get('https://ipapi.co/json/');
            lat = ipRes.data.latitude;
            lng = ipRes.data.longitude;
            city = ipRes.data.city;
            console.log("Using IP fallback location:", lat, lng, city);
          } catch (e) {
            console.error("IP geolocation failed, using Delhi fallback");
            city = 'Delhi';
          }
        }

        // Fetch providers
        const placesRes = await placesService.nearby({
          lat,
          lng,
          city,
          specialist_type: specialist,
          limit: 8,
        });
        setProviders(placesRes.data.results || []);
      } catch (err) {
        console.error(err);
      } finally {
        setIsLoading(false);
      }
    };
    fetchData();
  }, [router]);

  const urgency = analysis?.urgency_level || 'moderate';
  const specialist = analysis?.specialist_type || analysis?.specialists?.[0] || 'Specialist';
  const explanation = analysis?.specialist_explanation || 'Based on your symptoms, we found the best providers near you.';

  return (
    <>
      {/* ── Overlay ── */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black/40 backdrop-blur-sm z-40 transition-opacity"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* ── Sidebar ── */}
      <aside
        className={`fixed top-0 left-0 h-full w-72 bg-surface/95 backdrop-blur-2xl border-r border-white/20 z-50 flex flex-col shadow-2xl transition-transform duration-300 ease-in-out ${
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        <div className="flex items-center justify-between px-6 py-5 border-b border-white/10">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-primary rounded-xl flex items-center justify-center">
              <span className="material-symbols-outlined text-white text-lg">medical_services</span>
            </div>
            <span className="font-headline-sm text-headline-sm text-primary font-bold">MedLife</span>
          </div>
          <button onClick={() => setSidebarOpen(false)} className="p-2 hover:bg-primary/10 rounded-full transition-colors">
            <span className="material-symbols-outlined text-on-surface-variant">close</span>
          </button>
        </div>

        <nav className="flex-1 px-4 py-6 space-y-1 overflow-y-auto">
          <Link href="/" className="flex items-center gap-4 px-4 py-3 rounded-2xl text-on-surface-variant hover:bg-primary/5 hover:text-primary transition-all font-label-lg text-label-lg" onClick={() => setSidebarOpen(false)}>
            <span className="material-symbols-outlined">home</span>
            <span>Home</span>
          </Link>
          <Link href="/search" className="flex items-center gap-4 px-4 py-3 rounded-2xl text-on-surface-variant hover:bg-primary/5 hover:text-primary transition-all font-label-lg text-label-lg" onClick={() => setSidebarOpen(false)}>
            <span className="material-symbols-outlined">search</span>
            <span>Search Doctors</span>
          </Link>
          <Link href="/results" className="flex items-center gap-4 px-4 py-3 rounded-2xl bg-primary/10 text-primary font-label-lg text-label-lg" onClick={() => setSidebarOpen(false)}>
            <span className="material-symbols-outlined">history</span>
            <span>Results</span>
          </Link>
          <a href="#" className="flex items-center gap-4 px-4 py-3 rounded-2xl text-on-surface-variant hover:bg-primary/5 hover:text-primary transition-all font-label-lg text-label-lg" onClick={() => setSidebarOpen(false)}>
            <span className="material-symbols-outlined">bookmark</span>
            <span>Saved</span>
          </a>
          <Link href="/profile" className="flex items-center gap-4 px-4 py-3 rounded-2xl text-on-surface-variant hover:bg-primary/5 hover:text-primary transition-all font-label-lg text-label-lg" onClick={() => setSidebarOpen(false)}>
            <span className="material-symbols-outlined">person</span>
            <span>Profile</span>
          </Link>
        </nav>

        <div className="px-4 pb-6 pt-4 border-t border-white/10">
          <a href="#" className="flex items-center gap-4 px-4 py-3 rounded-2xl text-error hover:bg-error/5 transition-all font-label-lg text-label-lg">
            <span className="material-symbols-outlined">logout</span>
            <span>Logout</span>
          </a>
        </div>
      </aside>

      {/* ── Header ── */}
      <header className="fixed top-0 w-full z-40 bg-surface/80 backdrop-blur-xl border-b border-white/20 shadow-[0_4px_30px_rgba(43,76,190,0.04)] h-16 flex items-center px-4 md:px-8">
        <div className="flex justify-between items-center w-full">
          <div className="flex items-center gap-4">
            <button
              onClick={() => setSidebarOpen(true)}
              className="p-2 rounded-full hover:bg-primary/5 active:scale-95 transition-all"
            >
              <span className="material-symbols-outlined text-primary">menu</span>
            </button>
            <div className="flex items-center gap-2">
              <div className="w-7 h-7 bg-primary rounded-lg flex items-center justify-center">
                <span className="material-symbols-outlined text-white text-base">medical_services</span>
              </div>
              <span className="font-bold text-primary text-lg tracking-tight hidden sm:block">MedLife</span>
            </div>
          </div>
          <Link
            href="/search"
            className="flex items-center gap-2 px-4 py-2 rounded-full text-on-surface-variant hover:bg-primary/5 text-sm font-medium transition-all"
          >
            <span className="material-symbols-outlined text-base">arrow_back</span>
            New Search
          </Link>
        </div>
      </header>

      {/* ── Main ── */}
      <main className="pt-24 pb-16 px-4 md:px-8 max-w-7xl mx-auto min-h-screen">
        
        {/* Analysis Summary Banner */}
        {analysis && (
          <section className="mb-8 entrance-anim">
            <div className={`glass rounded-3xl p-6 glass-border border ${urgency === 'emergency' ? 'border-red-200 bg-red-50/20' : 'border-primary/10'}`}>
              <div className="md:flex items-center justify-between gap-6">
                <div className="flex items-start gap-4">
                  <div className={`w-12 h-12 rounded-2xl flex items-center justify-center shrink-0 ${urgency === 'emergency' ? 'bg-red-100' : 'bg-primary/10'}`}>
                    <span className={`material-symbols-outlined text-2xl ${urgency === 'emergency' ? 'text-red-600' : 'text-primary'}`}>
                      {urgency === 'emergency' ? 'emergency' : 'clinical_notes'}
                    </span>
                  </div>
                  <div>
                    <div className="flex items-center gap-3 mb-1 flex-wrap">
                      <h1 className="font-headline-md text-headline-md text-on-background">
                        Recommended: {specialist}
                      </h1>
                      <span className={`px-3 py-0.5 rounded-full text-label-sm font-label-lg border ${URGENCY_COLOR[urgency] || URGENCY_COLOR.moderate}`}>
                        {urgency.charAt(0).toUpperCase() + urgency.slice(1)} Urgency
                      </span>
                    </div>
                    <p className="text-body-md text-on-surface-variant">{explanation}</p>
                  </div>
                </div>
                <Link
                  href="/search"
                  className="mt-4 md:mt-0 glass px-6 py-2.5 rounded-full flex items-center gap-2 hover:bg-white transition-all text-on-surface-variant font-label-lg text-label-lg shadow-sm shrink-0"
                >
                  <span className="material-symbols-outlined text-[18px]">search</span>
                  Refine Search
                </Link>
              </div>
            </div>
          </section>
        )}

        {/* Results Grid */}
        <section>
          <div className="flex items-center justify-between mb-6">
            <h2 className="font-headline-lg text-headline-lg text-on-background">
              {isLoading ? 'Finding Nearby Specialists...' : `${providers.length} Providers Found`}
            </h2>
            {!isLoading && providers.length > 0 && (
              <span className="text-label-sm text-on-surface-variant">Ranked by reviews & rating</span>
            )}
          </div>

          {isLoading ? (
            <div className="space-y-4">
              {[1, 2, 3].map(i => (
                <div key={i} className="glass rounded-3xl p-6 animate-pulse">
                  <div className="flex gap-5">
                    <div className="w-44 h-44 rounded-2xl bg-surface-container-high shrink-0" />
                    <div className="flex-1 space-y-3 py-2">
                      <div className="h-5 bg-surface-container-high rounded-xl w-2/3" />
                      <div className="h-4 bg-surface-container-high rounded-xl w-1/3" />
                      <div className="h-4 bg-surface-container-high rounded-xl w-full" />
                      <div className="h-4 bg-surface-container-high rounded-xl w-4/5" />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : providers.length === 0 ? (
            <div className="glass rounded-3xl p-12 text-center">
              <span className="material-symbols-outlined text-5xl text-on-surface-variant mb-4 block">search_off</span>
              <h3 className="font-headline-md text-headline-md text-on-surface mb-2">No Providers Found</h3>
              <p className="text-on-surface-variant mb-6">We couldn&apos;t find any {specialist}s near your location.</p>
              <Link
                href="/search"
                className="bg-primary text-white px-8 py-3 rounded-full font-label-lg inline-flex items-center gap-2 hover:shadow-lg transition-all"
              >
                <span className="material-symbols-outlined text-sm">search</span>
                Try Another Search
              </Link>
            </div>
          ) : (
            <div className="space-y-5">
              {providers.map((p, i) => <ProviderCard key={i} p={p} onClick={() => setSelectedProvider(p)} />)}
            </div>
          )}
        </section>

        {/* Emergency Reminder */}
        {analysis?.emergency_mode && (
          <div className="mt-8 p-6 bg-red-50 border border-red-200 rounded-3xl flex items-start gap-4">
            <span className="material-symbols-outlined text-red-600 text-3xl shrink-0">emergency</span>
            <div>
              <h3 className="font-headline-sm text-headline-sm text-red-700 mb-1">This may be an Emergency</h3>
              <p className="text-red-600 mb-3">{analysis.urgency_reason}</p>
              <a href="tel:108" className="bg-red-600 text-white px-6 py-2.5 rounded-full font-label-lg inline-flex items-center gap-2 hover:bg-red-700 transition-all">
                <span className="material-symbols-outlined text-sm">call</span>
                Call 108 — Ambulance
              </a>
            </div>
          </div>
        )}
      </main>

      {/* ── Clinic Details Modal ── */}
      {selectedProvider && (
        <div className="fixed inset-0 z-[60] flex items-center justify-center p-4 sm:p-6">
          <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={() => setSelectedProvider(null)} />
          <div className="relative w-full max-w-3xl bg-surface rounded-3xl shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">
            <div className="flex items-center justify-between px-6 py-4 border-b border-outline-variant shrink-0">
              <h3 className="font-headline-sm text-headline-sm text-on-surface truncate pr-4">{selectedProvider.name}</h3>
              <button onClick={() => setSelectedProvider(null)} className="p-2 hover:bg-on-surface/5 rounded-full transition-colors shrink-0">
                <span className="material-symbols-outlined">close</span>
              </button>
            </div>
            
            <div className="flex-1 overflow-y-auto p-6">
              {isModalLoading ? (
                <div className="flex flex-col items-center justify-center py-12">
                  <span className="material-symbols-outlined text-primary text-4xl animate-spin mb-4">progress_activity</span>
                  <p className="text-on-surface-variant font-medium">Fetching details...</p>
                </div>
              ) : modalData ? (
                <div className="space-y-6">
                  <div className="space-y-4">
                    <h4 className="font-label-lg text-label-lg text-on-surface-variant">Contact & Location</h4>
                    <div className="flex items-start gap-3">
                      <span className="material-symbols-outlined text-primary">location_on</span>
                      <p className="text-body-md text-on-surface">{modalData.address}</p>
                    </div>
                    {modalData.phone && (
                      <div className="flex items-center gap-3">
                        <span className="material-symbols-outlined text-primary">call</span>
                        {modalData.phone === 'Contact Clinic directly' ? (
                          <span className="text-body-md text-on-surface-variant italic">Contact Clinic directly</span>
                        ) : (
                          <a href={`tel:${modalData.phone}`} className="text-primary hover:underline text-body-md">{modalData.phone}</a>
                        )}
                      </div>
                    )}
                    {modalData.website && (
                      <div className="flex items-center gap-3">
                        <span className="material-symbols-outlined text-primary">language</span>
                        <a href={modalData.website} target="_blank" rel="noreferrer" className="text-primary hover:underline text-body-md truncate">{modalData.website}</a>
                      </div>
                    )}
                  </div>
                </div>
              ) : (
                <div className="text-center py-8 text-error">Failed to load details.</div>
              )}
            </div>
            
            <div className="p-4 border-t border-outline-variant bg-surface flex justify-end shrink-0 gap-3">
              <button onClick={() => setSelectedProvider(null)} className="px-6 py-2 rounded-full font-label-lg text-on-surface-variant hover:bg-on-surface/5 transition-colors">
                Close
              </button>
              {modalData?.maps_url && (
                <a href={modalData.maps_url} target="_blank" rel="noreferrer" className="px-6 py-2 bg-primary text-white rounded-full font-label-lg flex items-center gap-2 hover:bg-primary/90 transition-colors">
                  <span className="material-symbols-outlined text-sm">directions</span>
                  Get Directions
                </a>
              )}
            </div>
          </div>
        </div>
      )}
    </>
  );
}
