import { useEffect, useRef } from "react";
import L from "leaflet";
import type { EventItem } from "@/services/api";

import "leaflet/dist/leaflet.css";

interface MapSectionProps {
  city: string;
  aqi: number;
  events?: EventItem[];
}

const cityCoords: Record<string, [number, number]> = {
  Paris: [48.8566, 2.3522],
  Lyon: [45.764, 4.8357],
  Marseille: [43.2965, 5.3698],
  Toulouse: [43.6047, 1.4442],
  Nice: [43.7102, 7.262],
  Bordeaux: [44.8378, -0.5792],
  Rennes: [48.1173, -1.6778],
  Nantes: [47.2184, -1.5536],
  Strasbourg: [48.5734, 7.7521],
  Lille: [50.6292, 3.0573],
  Monaco: [43.7384, 7.4246],
};

const categoryIcons: Record<string, { emoji: string; color: string }> = {
  concert: { emoji: "🎵", color: "#f59e0b" },
  spectacle: { emoji: "🎭", color: "#ef4444" },
  exposition: { emoji: "🎨", color: "#8b5cf6" },
  conférence: { emoji: "🎤", color: "#3b82f6" },
  visite: { emoji: "🏛️", color: "#22c55e" },
  "événement": { emoji: "⭐", color: "#ec4899" },
};

const getCategoryIcon = (cat: string) => {
  const key = cat.toLowerCase().replace(/^:/, "");
  return categoryIcons[key] || { emoji: "📍", color: "#6b7280" };
};

const MapSection = ({ city, aqi, events }: MapSectionProps) => {
  const safeEvents = events ?? [];
  const mapRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<L.Map | null>(null);

  const coords = cityCoords[city] || [48.8566, 2.3522];

  useEffect(() => {
    if (!mapRef.current) return;

    if (mapInstanceRef.current) {
      mapInstanceRef.current.remove();
      mapInstanceRef.current = null;
    }

    const map = L.map(mapRef.current, {
      zoomControl: false,
      attributionControl: false,
    }).setView(coords, 13);

    L.tileLayer("https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png", {
      maxZoom: 19,
    }).addTo(map);

    L.control.zoom({ position: "bottomright" }).addTo(map);

    // City center marker (AQI)
    const markerColor = aqi <= 2 ? "#22c55e" : aqi <= 3 ? "#f59e0b" : "#ef4444";
    const cityIcon = L.divIcon({
      className: "custom-marker",
      html: `<div style="width:22px;height:22px;border-radius:50%;background:${markerColor};border:3px solid white;box-shadow:0 2px 10px rgba(0,0,0,0.3)"></div>`,
      iconSize: [22, 22],
      iconAnchor: [11, 11],
    });

    L.marker(coords, { icon: cityIcon })
        .addTo(map)
        .bindPopup(`<strong>${city}</strong><br/>AQI: ${aqi}`);

    // Event markers scattered around city center
    if (safeEvents.length > 0) {
      const eventGroup = L.layerGroup().addTo(map);

      safeEvents.forEach((event, i) => {
        // Spread events in a circle around city center
        const angle = (2 * Math.PI * i) / Math.max(safeEvents.length, 1);
        const radius = 0.008 + Math.random() * 0.012;
        const lat = coords[0] + Math.cos(angle) * radius;
        const lng = coords[1] + Math.sin(angle) * radius;

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
          " onmouseover="this.style.transform='scale(1.3)'" onmouseout="this.style.transform='scale(1)'">${emoji}</div>`,
          iconSize: [32, 32],
          iconAnchor: [16, 16],
        });

        const linkHtml = (event.url || event.link)
            ? `<br/><a href="${event.url || event.link}" target="_blank" rel="noopener" style="color:#3b82f6;font-size:11px;">Voir plus →</a>`
            : "";

        const dateStr = event.date || event.date_start || "";
        const dateHtml = dateStr
            ? `<br/><span style="font-size:10px;color:#888;">${new Date(dateStr).toLocaleDateString("fr-FR", { day: "numeric", month: "short" })}</span>`
            : "";

        L.marker([lat, lng], { icon: eventIcon })
            .addTo(eventGroup)
            .bindPopup(
                `<div style="min-width:140px;">
              <strong style="font-size:12px;">${event.title}</strong>
              ${dateHtml}
              ${event.location || event.location_name ? `<br/><span style="font-size:10px;color:#666;">📍 ${event.location || event.location_name}</span>` : ""}
              ${linkHtml}
            </div>`,
                { closeButton: false, className: "event-popup" }
            );
      });
    }

    mapInstanceRef.current = map;

    setTimeout(() => {
      map.invalidateSize();
    }, 300);

    return () => {
      map.remove();
      mapInstanceRef.current = null;
    };
  }, [city, aqi, safeEvents]);

  return (
      <div className="dashboard-card overflow-hidden p-0">
        <div className="flex items-center justify-between p-4 pb-2">
          <h3 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground">
            Carte — {city}
          </h3>
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