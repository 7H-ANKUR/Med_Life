'use client'
import { useState, useMemo, useRef, useEffect } from 'react'
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet'
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

interface DraggableMapProps {
  initialLat: number;
  initialLng: number;
  onLocationSelect: (lat: number, lng: number) => void;
}

// Helper to update map center when initial location changes (e.g. from geolocation)
function MapCenterUpdater({ center }: { center: [number, number] }) {
  const map = useMap();
  useEffect(() => {
    map.setView(center);
  }, [center, map]);
  return null;
}

export default function DraggableMap({ initialLat, initialLng, onLocationSelect }: DraggableMapProps) {
  const [position, setPosition] = useState({ lat: initialLat, lng: initialLng });
  const markerRef = useRef<L.Marker>(null);

  // Sync initial props to state
  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setPosition({ lat: initialLat, lng: initialLng });
  }, [initialLat, initialLng]);

  const eventHandlers = useMemo(
    () => ({
      dragend() {
        const marker = markerRef.current;
        if (marker != null) {
          const newPos = marker.getLatLng();
          setPosition(newPos);
          onLocationSelect(newPos.lat, newPos.lng);
        }
      },
    }),
    [onLocationSelect],
  );

  return (
    <MapContainer 
      center={[initialLat, initialLng]} 
      zoom={13} 
      style={{ height: '100%', width: '100%', borderRadius: 'inherit' }}
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      <MapCenterUpdater center={[initialLat, initialLng]} />
      <Marker
        draggable={true}
        eventHandlers={eventHandlers}
        position={position}
        ref={markerRef}
        icon={icon}
      >
        <Popup minWidth={90}>
          <span>Drag to set your location</span>
        </Popup>
      </Marker>
    </MapContainer>
  )
}
