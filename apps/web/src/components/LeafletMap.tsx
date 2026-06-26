'use client'
import { useEffect } from 'react'
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

// Fix for default Leaflet icon in Next.js
const icon = L.icon({
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  tooltipAnchor: [16, -28],
  shadowSize: [41, 41]
});

export default function LeafletMap({ lat, lng, places }: { lat?: number; lng?: number; places: any[] }) {
  const centerLat = lat ?? 30.7046;
  const centerLng = lng ?? 76.7179;

  return (
    <MapContainer 
      center={[centerLat, centerLng]} 
      zoom={13} 
      style={{ height: '100%', width: '100%', borderRadius: 'inherit' }}
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      
      {/* User Location Marker */}
      <Marker position={[centerLat, centerLng]} icon={icon}>
        <Popup>You are here</Popup>
      </Marker>

      {/* Places Markers */}
      {places.slice(0, 10).map((p, i) => {
        if (!p.location || !p.location.lat || !p.location.lng) return null;
        return (
          <Marker 
            key={p.place_id || i} 
            position={[p.location.lat, p.location.lng]}
            icon={icon}
          >
            <Popup>
              <strong>{p.name}</strong><br/>
              {p.place_type}
            </Popup>
          </Marker>
        )
      })}
    </MapContainer>
  )
}
