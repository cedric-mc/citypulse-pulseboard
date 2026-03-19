import { useEffect, useRef } from "react";
import L from "leaflet";
import type { EventItem } from "@/services/api";
import "leaflet/dist/leaflet.css";

interface MapSectionProps {
  city:    string;
  aqi:     number;
  events?: EventItem[];
}

// Cache statique des villes connues — évite un appel Nominatim inutile
// pour les villes les plus fréquentes du dashboard
const CITY_COORDS_CACHE: Record<string, [number, number]> = {
  Paris:       [48.8566,  2.3522],
  Lyon:        [45.7640,  4.8357],
  Marseille:   [43.2965,  5.3698],
  Toulouse:    [43.6047,  1.4442],
  Nice:        [43.7102,  7.2620],
  Bordeaux:    [44.8378, -0.5792],
  Rennes:      [48.1173, -1.6778],
  Nantes:      [47.2184, -1.5536],
  Strasbourg:  [48.5734,  7.7521],
  Lille:       [50.6292,  3.0573],
  Angers:      [47.4784, -0.5632],
  Monaco:      [43.7384,  7.4246],
  Pau:         [43.2951, -0.3708],
  Grenoble:    [45.1885,  5.7245],
  Montpellier: [43.6108,  3.8767],
  Dijon:       [47.3220,  5.0415],
  Nancy:       [48.6921,  6.1844],
  Brest:       [48.3904, -4.4861],
  Tours:       [47.3941,  0.6848],
  Rouen:       [49.4432,  1.0993],
};

// Cache dynamique pour les villes géolocalisées via Nominatim
// Persiste en mémoire pendant la session — évite les appels répétés
const dynamicCoordsCache: Record<string, [number, number]> = {};

// Géolocalisation dynamique via OpenStreetMap Nominatim (gratuit, sans clé)
// Ordre de priorité : cache statique → cache dynamique → Nominatim → fallback Paris
async function getCityCoords(city: string): Promise<[number, number]> {
  // 1 — Cache statique (villes fréquentes, instantané)
  if (CITY_COORDS_CACHE[city]) return CITY_COORDS_CACHE[city];

  // 2 — Cache dynamique (déjà géolocalisé dans cette session)
  if (dynamicCoordsCache[city]) return dynamicCoordsCache[city];

  // 3 — Appel Nominatim pour les villes inconnues
  try {
    const res = await fetch(
      `https://nominatim.openstreetmap.org/search?city=${encodeURIComponent(city)}&country=France&format=json&limit=1`,
      { headers: { "Accept-Language": "fr", "User-Agent": "PulseBoard/1.0" } }
    );
    const data = await res.json();
    if (data.length > 0) {
      const coords: [number, number] = [parseFloat(data[0].lat), parseFloat(data[0].lon)];
      // Stocke en cache dynamique pour les prochains appels
      dynamicCoordsCache[city] = coords;
      return coords;
    }
  } catch {
    // Fallback silencieux sur Paris si Nominatim échoue
  }

  // 4 — Fallback Paris
  return [48.8566, 2.3522];
}

// Icônes emoji par catégorie d'événement
// Couleur du marqueur correspondante
const categoryIcons: Record<string, { emoji: string; color: string }> = {
  concert:     { emoji: "🎵", color: "#f59e0b" },
  spectacle:   { emoji: "🎭", color: "#ef4444" },
  exposition:  { emoji: "🎨", color: "#8b5cf6" },
  conférence:  { emoji: "🎤", color: "#3b82f6" },
  visite:      { emoji: "🏛️", color: "#22c55e" },
  "événement": { emoji: "⭐", color: "#ec4899" },
};

const getCategoryIcon = (cat: string) => {
  const key = cat.toLowerCase().replace(/^:/, "");
  return categoryIcons[key] || { emoji: "📍", color: "#6b7280" };
};

const MapSection = ({ city, aqi, events }: MapSectionProps) => {
  // Fallback tableau vide si events non fourni
  const safeEvents     = events ?? [];
  const mapRef         = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<L.Map | null>(null);

  useEffect(() => {
    if (!mapRef.current) return;

    // Détruit la carte précédente si elle existe
    if (mapInstanceRef.current) {
      mapInstanceRef.current.remove();
      mapInstanceRef.current = null;
    }

    // Couleur du marqueur centre ville selon l'AQI
    const markerColor = aqi <= 2 ? "#22c55e" : aqi <= 3 ? "#f59e0b" : "#ef4444";

    // Récupère les coords (cache statique → Nominatim) puis initialise la carte
    getCityCoords(city).then((coords) => {
      if (!mapRef.current) return;

      const map = L.map(mapRef.current, {
        zoomControl:        false,
        attributionControl: false,
      }).setView(coords, 13);

      L.tileLayer("https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png", {
        maxZoom: 19,
      }).addTo(map);

      L.control.zoom({ position: "bottomright" }).addTo(map);

      // ── Contour réel de la ville via Nominatim (GeoJSON) ──
      // Fallback cercle si le contour n'est pas disponible
      const fetchBoundary = async () => {
        try {
          const res = await fetch(
            `https://nominatim.openstreetmap.org/search?q=${encodeURIComponent(city)},France&format=json&polygon_geojson=1&limit=1`,
            { headers: { "User-Agent": "PulseBoard/1.0" } }
          );
          const data = await res.json();
          if (data?.[0]?.geojson) {
            L.geoJSON(data[0].geojson, {
              style: {
                color:       "#22c55e",
                weight:      2,
                opacity:     0.5,
                fillColor:   "#22c55e",
                fillOpacity: 0.12,
              },
            }).addTo(map);
          }
        } catch {
          // Fallback cercle si boundary fetch échoue
          L.circle(coords, {
            radius:      3000,
            color:       "#22c55e",
            weight:      2,
            opacity:     0.4,
            fillColor:   "#22c55e",
            fillOpacity: 0.12,
          }).addTo(map);
        }
      };
      fetchBoundary();

      // ── Marqueur centre ville avec couleur AQI ──
      const cityIcon = L.divIcon({
        className: "custom-marker",
        html: `<div style="width:22px;height:22px;border-radius:50%;background:${markerColor};border:3px solid white;box-shadow:0 2px 10px rgba(0,0,0,0.3)"></div>`,
        iconSize:   [22, 22],
        iconAnchor: [11, 11],
      });

      L.marker(coords, { icon: cityIcon })
        .addTo(map)
        .bindPopup(`<strong>${city}</strong><br/>AQI: ${aqi}`);

      // ── Marqueurs des événements ──────────────────────────
      // Utilise les vraies coordonnées GPS retournées par OpenAgenda
      // si disponibles — sinon fallback sur position aléatoire
      // autour du centre ville (event sans géolocalisation)
      if (safeEvents.length > 0) {
        const eventGroup = L.layerGroup().addTo(map);

        safeEvents.forEach((event, i) => {
          // ── Coordonnées du marqueur ──
          // Priorité 1 : vraies coords GPS de l'event (lat/lon OpenAgenda)
          // Priorité 2 : position aléatoire autour du centre ville
          let markerLat: number;
          let markerLng: number;

          if (event.lat && event.lon) {
            // ✅ Vraies coordonnées GPS — marqueur précis sur le lieu réel
            markerLat = event.lat;
            markerLng = event.lon;
          } else {
            // ⚠️ Pas de coords — position approchée en cercle autour du centre
            const angle  = (2 * Math.PI * i) / Math.max(safeEvents.length, 1);
            const radius = 0.008 + Math.random() * 0.012;
            markerLat    = coords[0] + Math.cos(angle) * radius;
            markerLng    = coords[1] + Math.sin(angle) * radius;
          }

          const { emoji, color } = getCategoryIcon(event.category || "");

          const eventIcon = L.divIcon({
            className: "event-marker",
            html: `<div style="
              display:flex;align-items:center;justify-content:center;
              width:32px;height:32px;border-radius:50%;
              background:${color};border:2px solid white;
              box-shadow:0 2px 8px rgba(0,0,0,0.25);
              font-size:14px;cursor:pointer;
              transition:transform 0.2s;
            " onmouseover="this.style.transform='scale(1.3)'"
              onmouseout="this.style.transform='scale(1)'">${emoji}</div>`,
            iconSize:   [32, 32],
            iconAnchor: [16, 16],
          });

          // Lien vers OpenAgenda si URL disponible
          const linkHtml = (event.url || event.link)
            ? `<br/><a href="${event.url || event.link}" target="_blank" rel="noopener" style="color:#3b82f6;font-size:11px;">Voir plus →</a>`
            : "";

          const dateStr  = event.date || event.date_start || "";
          const dateHtml = dateStr
            ? `<br/><span style="font-size:10px;color:#888;">${new Date(dateStr).toLocaleDateString("fr-FR", { day: "numeric", month: "short" })}</span>`
            : "";

          // Adresse réelle de l'event pour le popup
          // Priorité : address (complète) → location (nom du lieu)
          const locationHtml = (event.address || event.location || event.location_name)
            ? `<br/><span style="font-size:10px;color:#666;">📍 ${event.address || event.location || event.location_name}</span>`
            : "";

          L.marker([markerLat, markerLng], { icon: eventIcon })
            .addTo(eventGroup)
            .bindPopup(
              `<div style="min-width:140px;">
                <strong style="font-size:12px;">${event.title}</strong>
                ${dateHtml}
                ${locationHtml}
                ${linkHtml}
              </div>`,
              { closeButton: false, className: "event-popup" }
            );
        });
      }

      mapInstanceRef.current = map;

      // Fix rendu Leaflet après montage DOM
      setTimeout(() => map.invalidateSize(), 300);
    });

    return () => {
      if (mapInstanceRef.current) {
        mapInstanceRef.current.remove();
        mapInstanceRef.current = null;
      }
    };
  }, [city, aqi, safeEvents]);

  return (
    <div className="dashboard-card overflow-hidden p-0">
      <div className="flex items-center justify-between p-4 pb-2">
        <h3 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground">
          Carte — {city}
        </h3>
        {/* Badge nombre d'événements sur la carte */}
        {safeEvents.length > 0 && (
          <span className="rounded-full bg-primary/10 px-2.5 py-0.5 text-[10px] font-semibold text-primary">
            {safeEvents.length} événement{safeEvents.length !== 1 ? "s" : ""}
          </span>
        )}
      </div>
      <div ref={mapRef} className="h-64 w-full md:h-80 leaflet-container-fix" />
    </div>
  );
};

export default MapSection;