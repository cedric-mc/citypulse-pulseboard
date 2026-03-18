export interface CityData {
  id: string;
  name: string;
  country: string;
  coordinates: [number, number];
}

export interface WeatherData {
  temperature: number;
  feelsLike: number;
  humidity: number;
  windSpeed: number;
  windDirection: string;
  condition: string;
  icon: string;
  hourlyForecast: { hour: string; temp: number }[];
}

export interface AirQualityData {
  aqi: number;
  pm25: number;
  no2: number;
  level: "good" | "moderate" | "unhealthy" | "hazardous";
  recommendation: string;
}

export interface EventData {
  id: string;
  name: string;
  date: string;
  location: string;
  category: string;
}

export interface PredictionData {
  type: "air_quality" | "temperature";
  predictions: { hour: string; value: number; confidence: number }[];
}

export interface UrbanScoreData {
  score: number;
  criteria: {
    weather: number;
    airQuality: number;
    events: number;
  };
}

export const cities: CityData[] = [
  { id: "paris", name: "Paris", country: "France", coordinates: [48.8566, 2.3522] },
];

export const mockWeather: Record<string, WeatherData> = {
  paris: {
    temperature: 18,
    feelsLike: 16,
    humidity: 62,
    windSpeed: 14,
    windDirection: "SO",
    condition: "Partiellement nuageux",
    icon: "partly-cloudy",
    hourlyForecast: [
      { hour: "00h", temp: 14 }, { hour: "02h", temp: 13 }, { hour: "04h", temp: 12 },
      { hour: "06h", temp: 12 }, { hour: "08h", temp: 14 }, { hour: "10h", temp: 16 },
      { hour: "12h", temp: 18 }, { hour: "14h", temp: 20 }, { hour: "16h", temp: 19 },
      { hour: "18h", temp: 17 }, { hour: "20h", temp: 16 }, { hour: "22h", temp: 15 },
    ],
  },
};

export const mockAirQuality: Record<string, AirQualityData> = {
  paris: {
    aqi: 72,
    pm25: 18.5,
    no2: 32,
    level: "moderate",
    recommendation: "Qualité acceptable. Les personnes sensibles devraient limiter les activités prolongées en extérieur.",
  },
};

export const mockEvents: Record<string, EventData[]> = {
  paris: [
    { id: "1", name: "Nuit Blanche 2026", date: "2026-03-21", location: "Tout Paris", category: "Art & Culture" },
    { id: "2", name: "Marathon de Paris", date: "2026-04-05", location: "Champs-Élysées", category: "Sport" },
    { id: "3", name: "Festival Jazz à Saint-Germain", date: "2026-03-28", location: "Saint-Germain-des-Prés", category: "Musique" },
    { id: "4", name: "Salon de l'Agriculture", date: "2026-03-22", location: "Porte de Versailles", category: "Exposition" },
    { id: "5", name: "Marché Bio du Marais", date: "2026-03-18", location: "Place des Vosges", category: "Marché" },
  ],
};

export const mockPredictions: Record<string, PredictionData> = {
  paris: {
    type: "air_quality",
    predictions: [
      { hour: "+1h", value: 70, confidence: 92 },
      { hour: "+2h", value: 68, confidence: 88 },
      { hour: "+3h", value: 65, confidence: 82 },
      { hour: "+4h", value: 61, confidence: 75 },
      { hour: "+5h", value: 58, confidence: 68 },
      { hour: "+6h", value: 55, confidence: 60 },
    ],
  },
};

export const mockScores: Record<string, UrbanScoreData> = {
  paris: {
    score: 74,
    criteria: {
      weather: 82,
      airQuality: 65,
      events: 78,
    },
  },
};
