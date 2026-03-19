// ============================================================
// services/api.ts — Client HTTP vers le backend CityPulse
// Toutes les fonctions de fetch vers le backend FastAPI
// Types TypeScript pour toutes les réponses API
// ============================================================

// ── URL de base ────────────────────────────────────────────
// En local : fallback sur http://127.0.0.1:8000
// En prod  : défini dans front/.env via VITE_API_BASE
// ⚠️ À changer dans front/.env avant déploiement Render/Android
const API_BASE    = import.meta.env.VITE_API_BASE || "http://127.0.0.1:8000";

// Backend ML séparé — prédictions IA (toujours sur Render)
// Fallback sur l'URL Render si VITE_ML_API_BASE non défini
const ML_API_BASE = import.meta.env.VITE_ML_API_BASE || "https://citypulse-pulseboard-bqkl.onrender.com";

// ── Fonction utilitaire ────────────────────────────────────
// Wrapper fetch générique avec gestion d'erreur HTTP
async function fetchJson<T>(url: string): Promise<T> {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`API error: ${res.status} ${res.statusText}`);
  return res.json();
}

// ── Types des réponses API ─────────────────────────────────

export interface WeatherApiResponse {
  city:        string;
  temperature: number;
  feels_like:  number;
  humidity:    number;
  wind_speed:  number;
  description: string;
  icon:        string;
  icon_url?:   string;
  measured_at?: string;
  source?:     string;
}

export interface ForecastEntry {
  time:        string;
  temperature: number;
  feels_like:  number;
  humidity:    number;
  description: string;
  icon:        string;
  icon_url:    string;
}

export interface ForecastApiResponse {
  city:      string;
  forecasts: ForecastEntry[];
}

export interface AirQualityApiResponse {
  city:       string;
  aqi:        number;
  status:     string;
  color_code: string;
  pollutants: {
    pm25: number;
    no2:  number;
    o3:   number;
    co?:  number;
  };
  measured_at?: string;
  source?:      string;
}

export interface EventItem {
  id?:               number;
  title:             string;
  description?:      string | null;
  date?:             string;
  time?:             string;
  date_start?:       string;
  date_end?:         string;
  location?:         string;
  location_name?:    string;
  location_address?: string;
  address?:          string;   // ← adresse complète retournée par OpenAgenda
  city?:             string;
  category:          string;
  image?:            string | null;
  link?:             string;
  url?:              string;   // ← URL directe OpenAgenda
  // Coordonnées GPS réelles de l'event retournées par OpenAgenda
  // Utilisées par MapSection pour placer les marqueurs précisément
  // sur la carte au lieu de positions aléatoires
  lat?:              number | null;
  lon?:              number | null;
  source?:           string;
}

export type EventsApiResponse = EventItem[];

export interface ScoreDetails {
  weather_score: number;
  air_score:     number;
  events_score:  number;
}

export interface UrbanScoreApiResponse {
  city:    string;
  score:   number;
  details: ScoreDetails;
  source?: string;
}

// ── Prédictions ML ─────────────────────────────────────────
export interface PredictionEntry {
  hour:                  number;
  datetime:              string;
  predicted_temperature: number;
}

export interface PredictionApiResponse {
  city:        string;
  predictions: PredictionEntry[];
  confidence:  number;
  model_mae:   number;
}

// ── Fonctions de fetch ─────────────────────────────────────

// Météo actuelle
export const getWeather = (city: string) =>
  fetchJson<WeatherApiResponse>(`${API_BASE}/api/weather/${city}`);

// Prévisions 24h
export const getForecast = (city: string) =>
  fetchJson<ForecastApiResponse>(`${API_BASE}/api/forecast/${city}`);

// Qualité de l'air
export const getAirQuality = (city: string) =>
  fetchJson<AirQualityApiResponse>(`${API_BASE}/api/air/${city}`);

// Événements à venir — retourne lat/lon réels pour la carte
export const getEvents = (city: string) =>
  fetchJson<EventsApiResponse>(`${API_BASE}/api/events/${city}`);

// Score urbain
export const getUrbanScore = (city: string) =>
  fetchJson<UrbanScoreApiResponse>(`${API_BASE}/api/score/${city}`);

// Prédictions IA — endpoint ML séparé
export const getPredictions = (city: string, hours: number = 6) =>
  fetchJson<PredictionApiResponse>(`${ML_API_BASE}/api/predict/${city}?hours=${hours}`);