import re

file_path = 'apps/web/src/app/results/page.tsx'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# I want to add a ProviderCard component outside ResultsPage
provider_card_code = """
function ProviderCard({ p }: { p: any }) {
  const [details, setDetails] = useState<any>(null);

  useEffect(() => {
    let mounted = true;
    if (p.place_id) {
      placesService.detail(p.place_id).then(res => {
        if (mounted) {
          setDetails(res.data);
        }
      }).catch(err => console.error("Failed to load details", err));
    }
    return () => { mounted = false; };
  }, [p.place_id]);

  const phone = details?.phone || p.phone;
  const photo_url = (details?.photos && details.photos.length > 0) ? details.photos[0] : p.photo_url;

  return (
    <div className="glass glass-edge p-gutter rounded-[24px] flex flex-col md:flex-row gap-gutter group hover:shadow-[0_20px_40px_rgba(43,76,190,0.08)] transition-all stagger-in" >
      <div className="w-full md:w-48 h-48 rounded-2xl overflow-hidden shrink-0 relative">
        <div className="absolute inset-0 bg-cover bg-center" style={{ backgroundImage: `url(${photo_url || 'https://via.placeholder.com/400x400?text=Clinic'})` }} ></div>
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
          {phone && (
            <p className="text-on-surface-variant mb-2">
              <a href={`tel:${phone}`} className="text-primary hover:underline flex items-center gap-1">
                <span className="material-symbols-outlined text-sm">call</span>
                {phone}
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
  );
}

export default function ResultsPage() {
"""

content = content.replace("export default function ResultsPage() {", provider_card_code)

# Now replace the map loop with the new component
loop_regex = r"providers\.map\(\(p, i\) => \(\s*<div key=\{i\} className=\"glass glass-edge.*?\)\s*\)"
new_loop = "providers.map((p, i) => (<ProviderCard key={i} p={p} />))"
content = re.sub(loop_regex, new_loop, content, flags=re.DOTALL)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Done updating results/page.tsx with ProviderCard")
