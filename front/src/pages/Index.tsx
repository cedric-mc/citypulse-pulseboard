import { useState, useEffect, useCallback } from "react";
import { Activity, RefreshCw } from "lucide-react";
import CitySelector from "@/components/dashboard/CitySelector";
import UrbanScore from "@/components/dashboard/UrbanScore";
import WeatherCard from "@/components/dashboard/WeatherCard";
import AirQualityCard from "@/components/dashboard/AirQualityCard";
import EventsList from "@/components/dashboard/EventsList";
import PredictionCard from "@/components/dashboard/PredictionCard";
import MapSection from "@/components/dashboard/MapSection";
import DarkModeToggle from "@/components/dashboard/DarkModeToggle";
import { CardLoader, CardError } from "@/components/dashboard/CardStates";
import { useFetch } from "@/hooks/useFetch";
import { getWeather, getForecast, getAirQuality, getEvents, getUrbanScore } from "@/services/api";

const REFRESH_INTERVAL = 5 * 60 * 1000;

const Index = () => {
  const [selectedCity, setSelectedCity] = useState(
      localStorage.getItem("selectedCity") || "Paris"
  );
  const [lastUpdate, setLastUpdate] = useState(new Date());

  useEffect(() => {
    localStorage.setItem("selectedCity", selectedCity);
  }, [selectedCity]);

  const score = useFetch(() => getUrbanScore(selectedCity), [selectedCity]);
  const weather = useFetch(() => getWeather(selectedCity), [selectedCity]);
  const forecast = useFetch(() => getForecast(selectedCity), [selectedCity]);
  const air = useFetch(() => getAirQuality(selectedCity), [selectedCity]);
  const events = useFetch(() => getEvents(selectedCity), [selectedCity]);

  const refreshAll = useCallback(() => {
    score.refetch();
    weather.refetch();
    forecast.refetch();
    air.refetch();
    events.refetch();
    setLastUpdate(new Date());
  }, [score, weather, forecast, air, events]);

  useEffect(() => {
    const interval = setInterval(refreshAll, REFRESH_INTERVAL);
    return () => clearInterval(interval);
  }, [refreshAll]);

  return (
    <div className="min-h-screen bg-background">
      <header className="sticky top-0 z-50 border-b border-border bg-card/80 backdrop-blur-md">
        <div className="container flex h-14 items-center justify-between">
          <div className="flex items-center gap-2">
            <Activity className="h-5 w-5 text-primary" />
            <span className="text-lg font-bold text-foreground">
              Pulse<span className="text-primary">Board</span>
            </span>
          </div>
          <div className="flex items-center gap-2">
            <CitySelector selectedCity={selectedCity} onCityChange={setSelectedCity} />
            <button
              onClick={refreshAll}
              className="rounded-lg p-2 text-muted-foreground transition-colors hover:bg-secondary hover:text-foreground"
              title="Rafraîchir"
            >
              <RefreshCw className="h-4 w-4" />
            </button>
            <DarkModeToggle />
          </div>
        </div>
      </header>

      <main className="container py-6">
        <div className="mb-6 flex items-end justify-between">
          <div>
            <h1 className="text-2xl font-bold text-foreground">{selectedCity}</h1>
            <p className="text-sm text-muted-foreground">
              Tableau de bord urbain en temps réel — CityPulse
            </p>
          </div>
          <p className="text-[10px] text-muted-foreground">
            Mis à jour à {lastUpdate.toLocaleTimeString("fr-FR", { hour: "2-digit", minute: "2-digit" })}
          </p>
        </div>

        <div className="grid gap-5 md:grid-cols-2">
          {/* Score Urbain */}
          <div className="md:col-span-2">
            {score.loading ? <CardLoader /> : score.error ? <CardError message={score.error} onRetry={score.refetch} /> : score.data && <UrbanScore data={score.data} />}
          </div>

          {/* Weather */}
          <div className="md:col-span-2">
            {weather.loading ? <CardLoader /> : weather.error ? <CardError message={weather.error} onRetry={weather.refetch} /> : weather.data && <WeatherCard data={weather.data} forecast={forecast.data} city={selectedCity} />}
          </div>

          {/* Air Quality + Prediction */}
          {air.loading ? <CardLoader /> : air.error ? <CardError message={air.error} onRetry={air.refetch} /> : air.data && <AirQualityCard data={air.data} />}
          <PredictionCard />

          {/* Map */}
          <div className="md:col-span-2">
            <MapSection city={selectedCity} aqi={air.data?.aqi || 1} />
          </div>

          {/* Events */}
          <div className="md:col-span-2">
            {events.loading ? <CardLoader /> : events.error ? <CardError message={events.error} onRetry={events.refetch} /> : events.data && <EventsList data={events.data} />}
          </div>
        </div>
      </main>
    </div>
  );
};

export default Index;
