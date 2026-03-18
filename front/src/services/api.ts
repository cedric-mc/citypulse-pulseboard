const API_BASE = "https://citypulse-pulseboard.onrender.com";
const ML_API_BASE = "https://citypulse-pulseboard-bqkl.onrender.com";

async function fetchJson<T>(url: string): Promise<T> {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`API error: ${res.status} ${res.statusText}`);
  return res.json();
}

export interface WeatherApiResponse {
  city: string;
  temperature: number;
  feels_like: number;
  humidity: number;
  wind_speed: number;
  description: string;
  icon: string;
  icon_url?: string;
}

export interface ForecastEntry {
  time: string;
  temperature: number;
  feels_like: number;
  humidity: number;
  description: string;
  icon: string;
  icon_url: string;
}

export interface ForecastApiResponse {
  city: string;
  forecasts: ForecastEntry[];
}

export interface AirQualityApiResponse {
  city: string;
  aqi: number;
  status: string;
  color_code: string;
  pollutants: {
    pm25: number;
    no2: number;
    o3: number;
    co?: number;
  };
  measured_at?: string;
  source?: string;
}

export interface EventItem {
  id?: number;
  title: string;
  description?: string | null;
  date?: string;
  time?: string;
  date_start?: string;
  date_end?: string;
  location?: string;
  location_name?: string;
  location_address?: string;
  city?: string;
  category: string;
  image?: string | null;
  link?: string;
  url?: string;
  source?: string;
}

export type EventsApiResponse = EventItem[];

export interface ScoreDetails {
  weather_score: number;
  air_score: number;
  events_score: number;
}

export interface UrbanScoreApiResponse {
  city: string;
  score: number;
  details: ScoreDetails;
  source?: string;
}

// ── Prédictions ML (endpoint DAN) ──
export interface PredictionEntry {
  hour: number;
  datetime: string;
  predicted_temperature: number;
}

export interface PredictionApiResponse {
  city: string;
  predictions: PredictionEntry[];
  confidence: number;
  model_mae: number;
}

export const getWeather = (city: string) =>
  fetchJson<WeatherApiResponse>(`${API_BASE}/api/weather/${city}`);

export const getForecast = (city: string) =>
  fetchJson<ForecastApiResponse>(`${API_BASE}/api/forecast/${city}`);

export const getAirQuality = (city: string) =>
  fetchJson<AirQualityApiResponse>(`${API_BASE}/api/air/${city}`);

export const getEvents = (city: string) =>
  fetchJson<EventsApiResponse>(`${API_BASE}/api/events/${city}`);

export const getUrbanScore = (city: string) =>
  fetchJson<UrbanScoreApiResponse>(`${API_BASE}/api/score/${city}`);

export const getPredictions = (city: string, hours: number = 6) =>
  fetchJson<PredictionApiResponse>(`${ML_API_BASE}/api/predict/${city}?hours=${hours}`);