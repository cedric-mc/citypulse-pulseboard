import { useEffect, useRef } from "react";
import L from "leaflet";
import "leaflet/dist/leaflet.css";

interface MapSectionProps {
  city: string;
  aqi: number;
}

// Coordonnées GPS des villes connues — cache statique
// Évite un appel API de géolocalisation pour les villes fréquentes
const CITY_COORDS_CACHE: Record<string, [number, number]> = {
  Paris:      [48.8566,  2.3522],
  Lyon:       [45.7640,  4.8357],
  Marseille:  [43.2965,  5.3698],
  Toulouse:   [43.6047,  1.4442],
  Nice:       [43.7102,  7.2620],
  Bordeaux:   [44.8378, -0.5792],
  Rennes:     [48.1173, -1.6778],
  Nantes:     [47.2184, -1.5536],
  Strasbourg: [48.5734,  7.7521],
  Lille:      [50.6292,  3.0573],
  Angers:     [47.4784, -0.5632],
  Monaco:     [43.7384,  7.4246],
};

// Cache en mémoire pour les villes géolocalisées dynamiquement
const dynamicCoordsCache: Record<string, [number, number]> = {};

// Géolocalisation dynamique via OpenStreetMap Nominatim (gratuit, sans clé)
async function getCityCoords(city: string): Promise<[number, number]> {
  // 1 — Cache statique
  if (CITY_COORDS_CACHE[city]) return CITY_COORDS_CACHE[city];

  // 2 — Cache dynamique déjà résolu
  if (dynamicCoordsCache[city]) return dynamicCoordsCache[city];

  // 3 — Appel Nominatim pour les villes inconnues
  try {
    const res = await fetch(
      `https://nominatim.openstreetmap.org/search?city=${encodeURIComponent(city)}&country=France&format=json&limit=1`,
      { headers: { "Accept-Language": "fr" } }
    );
    const data = await res.json();
    if (data.length > 0) {
      const coords: [number, number] = [parseFloat(data[0].lat), parseFloat(data[0].lon)];
      dynamicCoordsCache[city] = coords;
      return coords;
    }
  } catch {
    // Fallback silencieux sur Paris
  }

  return [48.8566, 2.3522]; // Fallback Paris
}

const MapSection = ({ city, aqi }: MapSectionProps) => {
  const mapRef         = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<L.Map | null>(null);

  useEffect(() => {
    if (!mapRef.current) return;

    // Détruit la carte précédente si elle existe
    if (mapInstanceRef.current) {
      mapInstanceRef.current.remove();
      mapInstanceRef.current = null;
    }

    // Couleur du marqueur selon l'AQI
    const markerColor = aqi <= 2 ? "#22c55e" : aqi <= 3 ? "#f59e0b" : "#ef4444";

    // Récupère les coords puis initialise la carte
    getCityCoords(city).then((coords) => {
      if (!mapRef.current) return;

      const map = L.map(mapRef.current, {
        zoomControl:      false,
        attributionControl: false,
      }).setView(coords, 12);

      L.tileLayer("https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png", {
        maxZoom: 19,
      }).addTo(map);

      L.control.zoom({ position: "bottomright" }).addTo(map);

      const icon = L.divIcon({
        className: "custom-marker",
        html: `<div style="width:20px;height:20px;border-radius:50%;background:${markerColor};border:3px solid white;box-shadow:0 2px 8px rgba(0,0,0,0.3)"></div>`,
        iconSize:   [20, 20],
        iconAnchor: [10, 10],
      });

      L.marker(coords, { icon })
        .addTo(map)
        .bindPopup(`<strong>${city}</strong><br/>AQI: ${aqi}`);

      mapInstanceRef.current = map;

      // Fix rendu Leaflet après montage
      setTimeout(() => map.invalidateSize(), 300);
    });

    return () => {
      if (mapInstanceRef.current) {
        mapInstanceRef.current.remove();
        mapInstanceRef.current = null;
      }
    };
  }, [city, aqi]);

  return (
    <div className="dashboard-card overflow-hidden p-0">
      <div className="p-4 pb-2">
        <h3 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground">
          Carte — {city}
        </h3>
      </div>
      <div ref={mapRef} className="h-64 w-full md:h-80 leaflet-container-fix" />
    </div>
  );
};

export default MapSection;