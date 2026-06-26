import re

file_path = 'apps/web/src/app/results/page.tsx'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add imports and state
new_imports = """import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { placesService } from '@/services/api';
import axios from 'axios';

export default function ResultsPage() {
  const [analysis, setAnalysis] = useState<any>(null);
  const [providers, setProviders] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();

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
        
        const specialist = parsed.specialists && parsed.specialists.length > 0 ? parsed.specialists[0] : undefined;

        // Fetch location
        let lat, lng;
        try {
            const ipRes = await axios.get('https://ipapi.co/json/');
            lat = ipRes.data.latitude;
            lng = ipRes.data.longitude;
        } catch (e) {
            console.error("IPAPI failed", e);
        }

        // Fetch places
        const placesRes = await placesService.nearby({ lat, lng, specialist_type: specialist, limit: 5 });
        setProviders(placesRes.data.results || []);

      } catch (err) {
        console.error(err);
      } finally {
        setIsLoading(false);
      }
    };
    fetchData();
  }, [router]);
"""

content = re.sub(
    r"import React from 'react';\nimport Link from 'next/link';\n\nexport default function ResultsPage\(\) \{",
    new_imports,
    content
)

# 2. Replace the body of "Clinical Insights"
# We want to replace the list of symptoms and specialists.
# Currently the HTML has sections for "Primary Analysis", "Mapped Specialists".
# Let's replace the content starting from `<div className="space-y-4">` under "Primary Analysis"
# and also replace the "Mapped Specialists" section.
# Since it's easier to just replace the whole Clinical Insights div, I'll find its boundaries.

insight_regex = r'(<h2 className="font-headline-md text-headline-md text-on-background">Clinical Insights</h2>\s*</div>)(.*?)(<div className="bg-primary-container p-6 rounded-\[24px\] text-on-primary-container shadow-xl stagger-in" >)'

clinical_insight_dynamic = r"""\1
{isLoading ? (
  <div className="p-4 text-center">Loading insights...</div>
) : analysis ? (
  <>
    <div className="mb-6">
      <div className="flex justify-between items-end mb-4">
        <div>
          <h3 className="font-headline-md text-headline-md text-primary">Primary Analysis</h3>
          <p className="text-on-surface-variant text-label-sm">Based on your reported symptoms</p>
        </div>
      </div>
      <div className="space-y-4">
        {analysis.symptoms && analysis.symptoms.map((sym: string, i: number) => (
          <div key={i} className="flex items-start gap-3 bg-surface-container-lowest p-3 rounded-xl border border-outline-variant/30">
            <span className="material-symbols-outlined text-primary text-[20px] mt-0.5">vital_signs</span>
            <span className="text-body-md text-on-surface">{sym}</span>
          </div>
        ))}
      </div>
    </div>
    
    <div className="mb-6">
      <div className="flex justify-between items-end mb-4">
        <div>
          <h3 className="font-headline-md text-headline-md text-primary">Mapped Specialists</h3>
        </div>
      </div>
      <div className="space-y-4">
        {analysis.specialists && analysis.specialists.map((spec: string, i: number) => (
          <div key={i} className="flex items-start gap-3 bg-secondary-container/10 p-3 rounded-xl border border-secondary/10">
            <span className="material-symbols-outlined text-secondary text-[20px] mt-0.5">stethoscope</span>
            <span className="text-body-md text-on-surface">{spec}</span>
          </div>
        ))}
      </div>
    </div>
    
    {analysis.urgency && (
      <div className="mb-6">
        <div className="flex justify-between items-end mb-4">
          <div>
            <h3 className={`font-headline-md text-headline-md ${analysis.urgency.toLowerCase() === 'high' ? 'text-error' : 'text-primary'}`}>Urgency</h3>
          </div>
        </div>
        <p className="text-body-md text-on-surface">{analysis.urgency}</p>
      </div>
    )}
  </>
) : null}
\3"""

content = re.sub(insight_regex, clinical_insight_dynamic, content, flags=re.DOTALL)

# 3. Replace Recommended Providers
# Find the start of the Recommended Providers and replace until the end of that column.
providers_regex = r'(<h2 className="font-headline-md text-headline-md text-on-background">Recommended Providers</h2>\s*<button className="text-primary font-label-lg text-label-lg flex items-center gap-1 hover:underline">\s*View All \(24\)\s*<span className="material-symbols-outlined">chevron_right</span>\s*</button>\s*</div>)(.*?)(</div>\s*</div>\s*</div>\s*</main>)'

providers_dynamic = r"""\1
{isLoading ? (
  <div className="p-10 text-center">Finding best specialists nearby...</div>
) : providers.length === 0 ? (
  <div className="p-10 text-center">No providers found matching your criteria.</div>
) : (
  providers.map((p, i) => (
    <div key={i} className="glass glass-edge p-gutter rounded-[24px] flex flex-col md:flex-row gap-gutter group hover:shadow-[0_20px_40px_rgba(43,76,190,0.08)] transition-all stagger-in" >
      <div className="w-full md:w-48 h-48 rounded-2xl overflow-hidden shrink-0 relative">
        <div className="absolute inset-0 bg-cover bg-center" style={{ backgroundImage: `url(${p.photo_url || 'https://via.placeholder.com/400x400?text=Clinic'})` }} ></div>
        {i === 0 && <div className="absolute top-2 left-2 bg-primary/90 backdrop-blur-md text-white text-[10px] font-bold px-3 py-1 rounded-full">Top Rated</div>}
      </div>
      <div className="flex-1 flex flex-col justify-between">
        <div>
          <div className="flex justify-between items-start mb-2">
            <div>
              <h3 className="font-headline-md text-headline-md text-on-background group-hover:text-primary transition-colors">{p.name}</h3>
              <p className="text-tertiary font-label-lg text-label-lg">{p.speciality || p.place_type}</p>
            </div>
            {p.rating && (
              <div className="flex items-center gap-1 text-on-surface-variant bg-surface-container-high px-2 py-1 rounded-lg">
                <span className="material-symbols-outlined text-amber-500" >star</span>
                <span className="font-bold">{p.rating}</span>
              </div>
            )}
          </div>
          <div className="flex flex-wrap gap-2 mb-4">
            <span className="px-3 py-1 bg-surface-container rounded-full text-label-sm text-on-surface-variant">{p.address}</span>
          </div>
          {p.phone && (
            <p className="text-on-surface-variant mb-2">
              <a href={`tel:${p.phone}`} className="text-primary hover:underline flex items-center gap-1">
                <span className="material-symbols-outlined text-sm">call</span>
                {p.phone}
              </a>
            </p>
          )}
        </div>
        <div className="mt-6 flex flex-wrap gap-4 items-center justify-between">
          <div className="flex items-center gap-4">
            {p.distance_label && (
              <div className="flex items-center gap-2 text-on-surface-variant">
                <span className="material-symbols-outlined text-[18px]">location_on</span>
                <span className="text-label-lg font-label-lg">{p.distance_label}</span>
              </div>
            )}
          </div>
          <button onClick={() => { if(p.maps_url) window.open(p.maps_url, '_blank') }} className="px-8 py-3 bg-primary text-white rounded-full font-label-lg text-label-lg hover:shadow-lg hover:shadow-primary/30 transition-all active:scale-95">
            View on Map
          </button>
        </div>
      </div>
    </div>
  ))
)}
\3"""

content = re.sub(providers_regex, providers_dynamic, content, flags=re.DOTALL)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Done updating results/page.tsx")
