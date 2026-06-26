"use client";

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import dynamic from 'next/dynamic';
import { symptomsService } from '@/services/api';

const DraggableMap = dynamic(() => import('@/components/DraggableMap'), { ssr: false });

const QUICK_SYMPTOMS = [
  { label: 'Migraine', text: 'I have a severe migraine headache with light sensitivity and nausea' },
  { label: 'Lower Back Pain', text: 'I have persistent lower back pain radiating down my leg' },
  { label: 'Skin Rash', text: 'I have a red itchy skin rash that appeared suddenly' },
  { label: 'Chest Pain', text: 'I am experiencing chest pain and tightness' },
  { label: 'Fever', text: 'I have a high fever above 102F with chills and body aches' },
  { label: 'Anxiety', text: 'I am experiencing severe anxiety and panic attacks' },
];

export default function SearchPage() {
  const [symptoms, setSymptoms] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [mapOpen, setMapOpen] = useState(false);
  const [userLocation, setUserLocation] = useState<{lat: number, lng: number} | null>(null);
  const [locationName, setLocationName] = useState<string>('');
  const [tempLocation, setTempLocation] = useState<{lat: number, lng: number}>({ lat: 28.6139, lng: 77.2090 });
  const router = useRouter();

  useEffect(() => {
    if ("geolocation" in navigator) {
      navigator.geolocation.getCurrentPosition((pos) => {
        setTempLocation({ lat: pos.coords.latitude, lng: pos.coords.longitude });
      });
    }
  }, []);

  useEffect(() => {
    if (userLocation) {
      fetch(`https://nominatim.openstreetmap.org/reverse?lat=${userLocation.lat}&lon=${userLocation.lng}&format=json`)
        .then(res => res.json())
        .then(data => {
          if (data && data.display_name) {
            setLocationName(data.display_name);
          }
        })
        .catch(err => console.error('Geocoding failed:', err));
    } else {
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setLocationName('');
    }
  }, [userLocation]);

  const handleAnalyze = async () => {
    if (!symptoms.trim()) return;
    setIsLoading(true);
    try {
      const res = await symptomsService.analyze(symptoms);
      localStorage.setItem('lastAnalysis', JSON.stringify(res.data));
      if (userLocation) {
        localStorage.setItem('userLocation', JSON.stringify(userLocation));
      } else {
        localStorage.removeItem('userLocation');
      }
      router.push('/results');
    } catch (error) {
      console.error(error);
      alert('Failed to analyze symptoms. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const appendSymptom = (text: string) => {
    setSymptoms(text);
  };

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
        id="sidebar"
        className={`fixed top-0 left-0 h-full w-72 bg-surface/95 backdrop-blur-2xl border-r border-white/20 z-50 flex flex-col shadow-2xl transition-transform duration-300 ease-in-out ${
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        {/* Sidebar Header */}
        <div className="flex items-center justify-between px-6 py-5 border-b border-white/10">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-primary rounded-xl flex items-center justify-center">
              <span className="material-symbols-outlined text-white text-lg">medical_services</span>
            </div>
            <span className="font-headline-sm text-headline-sm text-primary font-bold">MedLife</span>
          </div>
          <button
            onClick={() => setSidebarOpen(false)}
            className="p-2 hover:bg-primary/10 rounded-full transition-colors"
          >
            <span className="material-symbols-outlined text-on-surface-variant">close</span>
          </button>
        </div>

        {/* Nav Links */}
        <nav className="flex-1 px-4 py-6 space-y-1 overflow-y-auto">
          <Link
            href="/"
            className="flex items-center gap-4 px-4 py-3 rounded-2xl text-on-surface-variant hover:bg-primary/5 hover:text-primary transition-all font-label-lg text-label-lg"
            onClick={() => setSidebarOpen(false)}
          >
            <span className="material-symbols-outlined">home</span>
            <span>Home</span>
          </Link>
          <Link
            href="/search"
            className="flex items-center gap-4 px-4 py-3 rounded-2xl bg-primary/10 text-primary font-label-lg text-label-lg"
            onClick={() => setSidebarOpen(false)}
          >
            <span className="material-symbols-outlined">search</span>
            <span>Search Doctors</span>
          </Link>
          <Link
            href="/results"
            className="flex items-center gap-4 px-4 py-3 rounded-2xl text-on-surface-variant hover:bg-primary/5 hover:text-primary transition-all font-label-lg text-label-lg"
            onClick={() => setSidebarOpen(false)}
          >
            <span className="material-symbols-outlined">history</span>
            <span>History</span>
          </Link>
          <a
            href="#"
            className="flex items-center gap-4 px-4 py-3 rounded-2xl text-on-surface-variant hover:bg-primary/5 hover:text-primary transition-all font-label-lg text-label-lg"
            onClick={() => setSidebarOpen(false)}
          >
            <span className="material-symbols-outlined">bookmark</span>
            <span>Saved</span>
          </a>
          <Link
            href="/profile"
            className="flex items-center gap-4 px-4 py-3 rounded-2xl text-on-surface-variant hover:bg-primary/5 hover:text-primary transition-all font-label-lg text-label-lg"
            onClick={() => setSidebarOpen(false)}
          >
            <span className="material-symbols-outlined">person</span>
            <span>Profile</span>
          </Link>
        </nav>

        {/* Sidebar Footer */}
        <div className="px-4 pb-6 pt-4 border-t border-white/10">
          <a
            href="#"
            className="flex items-center gap-4 px-4 py-3 rounded-2xl text-error hover:bg-error/5 transition-all font-label-lg text-label-lg"
          >
            <span className="material-symbols-outlined">logout</span>
            <span>Logout</span>
          </a>
        </div>
      </aside>

      {/* ── Top Header ── */}
      <header className="fixed top-0 w-full z-40 bg-surface/80 backdrop-blur-xl border-b border-white/20 shadow-[0_4px_30px_rgba(43,76,190,0.04)] h-16 flex items-center px-4 md:px-8">
        <div className="flex justify-between items-center w-full">
          <div className="flex items-center gap-4">
            <button
              id="menu-toggle"
              onClick={() => setSidebarOpen(true)}
              className="p-2 hover:bg-primary/5 transition-colors rounded-full active:scale-95 duration-200"
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
          <div className="flex items-center gap-2">
            <Link
              href="/results"
              className="hidden md:flex items-center gap-2 px-4 py-2 rounded-full text-on-surface-variant hover:bg-primary/5 text-sm font-medium transition-all"
            >
              <span className="material-symbols-outlined text-base">history</span>
              Recent
            </Link>
            <button className="w-9 h-9 rounded-full bg-primary/10 flex items-center justify-center hover:bg-primary/20 transition-all">
              <span className="material-symbols-outlined text-primary text-base">person</span>
            </button>
          </div>
        </div>
      </header>

      {/* ── Main Content ── */}
      <main className="relative pt-28 pb-16 px-4 md:px-8 max-w-7xl mx-auto overflow-hidden min-h-screen">
        {/* Background orbs */}
        <div className="ai-orb absolute -top-20 -right-20 w-[400px] h-[400px] rounded-full pointer-events-none opacity-40" />
        <div className="ai-orb absolute top-[40%] -left-40 w-[300px] h-[300px] rounded-full pointer-events-none opacity-30" />

        {/* Hero Section */}
        <section className="relative z-10 entrance-anim">
          <div className="text-center mb-10 max-w-3xl mx-auto">
            <div className="inline-block bg-tertiary/10 text-tertiary px-4 py-1 rounded-full mb-4 border border-tertiary/20">
              <span className="text-label-sm font-label-lg uppercase tracking-wider">AI-Powered Medical Triage</span>
            </div>
            <h1 className="font-display-lg text-display-lg text-primary mb-4">
              Find the Right Doctor
            </h1>
            <p className="font-body-lg text-body-lg text-on-surface-variant">
              Describe your symptoms and our AI maps them to the right specialist near you.
            </p>
          </div>

          {/* Search Card */}
          <div className="max-w-4xl mx-auto glass rounded-3xl p-6 shadow-[0_20px_50px_rgba(43,76,190,0.08)] glass-border mb-8">
            <div className="flex justify-between items-center mb-3 px-2">
              <span className="text-on-surface-variant text-label-lg font-medium">What&apos;s bothering you?</span>
              <button 
                onClick={() => setMapOpen(true)} 
                className="flex items-center gap-1 text-primary hover:bg-primary/5 px-3 py-1.5 rounded-full transition-all border border-primary/20 bg-primary/5 active:scale-95"
              >
                <span className="material-symbols-outlined text-sm">location_on</span>
                <span className="text-label-sm font-label-lg">
                  {userLocation ? 'Change Location' : 'Set Exact Location'}
                </span>
              </button>
            </div>
            
            {locationName && (
              <div className="mb-4 px-4 py-2 bg-primary/5 border border-primary/20 rounded-xl flex items-center gap-2">
                <span className="material-symbols-outlined text-primary text-sm">my_location</span>
                <span className="text-sm text-primary font-medium truncate" title={locationName}>
                  Searching near: {locationName}
                </span>
              </div>
            )}
            
            <div className="relative group">
              <textarea
                className="w-full bg-white/50 border-2 border-outline-variant focus:border-primary focus:ring-4 focus:ring-primary/10 rounded-2xl p-6 font-body-md text-body-md transition-all resize-none"
                placeholder="E.g., 'I have a sharp pain in my lower right abdomen that started yesterday with mild fever...'"
                rows={4}
                value={symptoms}
                onChange={(e) => setSymptoms(e.target.value)}
                onKeyDown={(e) => { if (e.key === 'Enter' && e.ctrlKey) handleAnalyze(); }}
              />
              <div className="absolute bottom-4 right-4 flex items-center gap-3">
                <span className="text-label-sm text-outline hidden md:block">{symptoms.length}/500</span>
                <button
                  id="analyze-btn"
                  onClick={handleAnalyze}
                  disabled={isLoading || !symptoms.trim()}
                  className="bg-primary hover:bg-primary/90 text-on-primary px-8 py-3 rounded-full flex items-center gap-2 font-label-lg text-label-lg transition-all active:scale-95 shadow-lg shadow-primary/20 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isLoading ? (
                    <>
                      <span className="animate-spin material-symbols-outlined text-sm">progress_activity</span>
                      Analyzing...
                    </>
                  ) : (
                    <>
                      Find Specialists
                      <span className="material-symbols-outlined text-sm">arrow_forward</span>
                    </>
                  )}
                </button>
              </div>
            </div>

            {/* Quick symptom pills */}
            <div className="mt-6 flex flex-wrap gap-2 items-center">
              <span className="text-label-sm font-label-lg text-on-surface-variant mr-1">Quick:</span>
              {QUICK_SYMPTOMS.map((qs) => (
                <button
                  key={qs.label}
                  id={`quick-${qs.label.toLowerCase().replace(/\s+/g, '-')}`}
                  onClick={() => appendSymptom(qs.text)}
                  className="px-4 py-2 rounded-full glass border border-primary/20 text-primary text-label-sm font-label-lg hover:bg-primary hover:text-white transition-all active:scale-95"
                >
                  {qs.label}
                </button>
              ))}
            </div>
          </div>
        </section>

        {/* How It Works */}
        <section className="mt-16 entrance-anim stagger-1">
          <div className="mb-8 text-center">
            <h2 className="font-headline-lg text-headline-lg text-on-surface">How MedLife Works</h2>
            <p className="text-body-md text-on-surface-variant mt-2">Simple 3-step process to the right specialist</p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {[
              {
                icon: 'psychology',
                color: 'primary',
                title: 'Describe Symptoms',
                desc: 'Type your symptoms in plain language. Our AI understands medical context from natural language.',
                insight: 'NLP symptom extraction active',
              },
              {
                icon: 'clinical_notes',
                color: 'secondary',
                title: 'AI Triage',
                desc: 'Our system maps your symptoms to the right specialist using a clinical decision engine.',
                insight: 'Evidence-based specialist matching',
              },
              {
                icon: 'location_on',
                color: 'tertiary',
                title: 'Find Nearby Doctors',
                desc: 'Get ranked clinics and hospitals near you with real ratings and contact details.',
                insight: 'Live Google Maps data via Apify',
              },
            ].map((step) => (
              <div
                key={step.title}
                className="glass rounded-3xl p-6 glass-border shadow-sm flex flex-col gap-4 entrance-anim"
              >
                <div className={`h-12 w-12 bg-${step.color}/10 rounded-xl flex items-center justify-center`}>
                  <span className={`material-symbols-outlined text-${step.color} text-3xl`}>{step.icon}</span>
                </div>
                <div className="space-y-2">
                  <h3 className="font-headline-md text-headline-md">{step.title}</h3>
                  <p className="text-body-md text-on-surface-variant">{step.desc}</p>
                </div>
                <div className="mt-auto pt-4 flex items-center text-tertiary font-label-lg gap-1">
                  <span className="material-symbols-outlined text-sm">verified</span>
                  {step.insight}
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Emergency CTA */}
        <section className="mt-16 entrance-anim stagger-4">
          <div className="glass rounded-[32px] p-8 glass-border overflow-hidden relative">
            <div className="absolute top-0 right-0 w-64 h-64 bg-error/5 rounded-full -translate-y-1/2 translate-x-1/2 pointer-events-none" />
            <div className="md:flex gap-8 items-center relative z-10">
              <div className="md:w-1/2 space-y-4">
                <h2 className="font-headline-lg text-headline-lg text-error">Need Emergency Help?</h2>
                <p className="text-body-lg text-on-surface-variant">
                  If you're experiencing severe symptoms — chest pain, difficulty breathing, stroke signs — call emergency services immediately.
                </p>
                <div className="flex flex-wrap gap-4">
                  <a
                    href="tel:108"
                    className="bg-error text-on-error px-6 py-3 rounded-full font-label-lg flex items-center gap-2 hover:opacity-90 transition-opacity active:scale-95"
                  >
                    <span className="material-symbols-outlined">call</span>
                    Call 108 — Ambulance
                  </a>
                  <a
                    href="tel:112"
                    className="glass border border-error/30 text-error px-6 py-3 rounded-full font-label-lg flex items-center gap-2 hover:bg-error/5 transition-all active:scale-95"
                  >
                    <span className="material-symbols-outlined">emergency</span>
                    National Emergency
                  </a>
                </div>
              </div>
              <div className="md:w-1/2 mt-6 md:mt-0 flex justify-center">
                <div className="relative w-48 h-48">
                  <div className="absolute inset-0 bg-error/10 rounded-full animate-ping opacity-30" />
                  <div className="absolute inset-4 bg-error/20 rounded-full flex items-center justify-center">
                    <span className="material-symbols-outlined text-error" style={{ fontSize: '80px' }}>local_hospital</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>
      </main>

      {/* ── Map Modal ── */}
      {mapOpen && (
        <div className="fixed inset-0 z-[60] flex items-center justify-center p-4 sm:p-6">
          <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={() => setMapOpen(false)} />
          <div className="relative w-full max-w-3xl bg-surface rounded-3xl shadow-2xl overflow-hidden flex flex-col h-[70vh] sm:h-[80vh]">
            <div className="flex items-center justify-between px-6 py-4 border-b border-outline-variant">
              <h3 className="font-headline-sm text-headline-sm text-on-surface">Set Your Exact Location</h3>
              <button onClick={() => setMapOpen(false)} className="p-2 hover:bg-on-surface/5 rounded-full transition-colors">
                <span className="material-symbols-outlined">close</span>
              </button>
            </div>
            <div className="flex-1 bg-surface-container-low relative">
              <DraggableMap 
                initialLat={tempLocation.lat} 
                initialLng={tempLocation.lng} 
                onLocationSelect={(lat, lng) => setTempLocation({ lat, lng })}
              />
            </div>
            <div className="p-4 border-t border-outline-variant flex justify-end gap-3 bg-surface">
              <button onClick={() => setMapOpen(false)} className="px-6 py-2 rounded-full font-label-lg text-on-surface-variant hover:bg-on-surface/5">
                Cancel
              </button>
              <button 
                onClick={() => {
                  setUserLocation(tempLocation);
                  setMapOpen(false);
                }} 
                className="px-6 py-2 rounded-full font-label-lg bg-primary text-on-primary hover:bg-primary/90"
              >
                Confirm Location
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
