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

// Rafraîchissement automatique toutes les 5 minutes
const REFRESH_INTERVAL = 5 * 60 * 1000;

// Délai avant retry automatique en cas d'erreur
// Render prend ~8s pour synchroniser une nouvelle ville
// donc on attend suffisamment avant de réessayer
const RETRY_DELAY = 8000;

// Nombre maximum de retries automatiques
// 5 tentatives × 8s = 40s max pour synchroniser une ville inconnue
const MAX_RETRIES = 5;

const Index = () => {
  const [selectedCity, setSelectedCity] = useState(
    localStorage.getItem("selectedCity") || "Paris"
  );
  const [lastUpdate, setLastUpdate] = useState(new Date());

  // Compteur de retry — incrémenté pour déclencher un nouveau fetch
  // Remis à zéro à chaque changement de ville
  const [retryCount, setRetryCount] = useState(0);

  // Persiste la ville sélectionnée en localStorage
  // et remet le retry à zéro pour la nouvelle ville
  useEffect(() => {
    localStorage.setItem("selectedCity", selectedCity);
    setRetryCount(0);
  }, [selectedCity]);

  // ── Données indépendantes ──────────────────────────────────
  // Météo, prévisions, qualité de l'air et events sont appelés
  // en parallèle dès le chargement ou changement de ville
  // Le backend synchronise à la volée via refresh_city_data
  const weather  = useFetch(() => getWeather(selectedCity),   [selectedCity, retryCount]);
  const forecast = useFetch(() => getForecast(selectedCity),  [selectedCity, retryCount]);
  const air      = useFetch(() => getAirQuality(selectedCity),[selectedCity, retryCount]);
  const events   = useFetch(() => getEvents(selectedCity),    [selectedCity, retryCount]);

  // ── Score urbain — dépendant de météo ET qualité de l'air ──
  // Le score nécessite que météo OU air soit disponible en BDD
  // pour pouvoir calculer le score global
  // On attend donc que l'une des deux données soit reçue
  // avant de déclencher l'appel au score
  const scoreReady = !!weather.data || !!air.data;
  const score = useFetch(
    () => getUrbanScore(selectedCity),
    [selectedCity, retryCount, scoreReady] // ← scoreReady déclenche le refetch
  );

  // ── Retry automatique ──────────────────────────────────────
  // Si une erreur est détectée et qu'on n'est pas en cours de chargement,
  // on attend RETRY_DELAY ms puis on incrémente retryCount
  // Ce qui force un nouveau fetch sur toutes les données
  // Utile pour les villes inconnues qui nécessitent une synchronisation
  useEffect(() => {
    const hasError  = weather.error || air.error || events.error;
    const isLoading = weather.loading || air.loading || events.loading || score.loading;

    if (hasError && !isLoading && retryCount < MAX_RETRIES) {
      const timer = setTimeout(() => {
        setRetryCount(prev => prev + 1);
      }, RETRY_DELAY);
      return () => clearTimeout(timer);
    }
  }, [
    weather.error, air.error, events.error, score.error,
    weather.loading, air.loading, events.loading, score.loading,
    retryCount
  ]);

  // ── Rafraîchissement manuel ────────────────────────────────
  // Déclenché par le bouton refresh ou automatiquement
  // toutes les 5 minutes via l'interval
  const refreshAll = useCallback(() => {
    score.refetch();
    weather.refetch();
    forecast.refetch();
    air.refetch();
    events.refetch();
    setLastUpdate(new Date());
  }, [score, weather, forecast, air, events]);

  // Rafraîchissement automatique toutes les 5 minutes
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

          {/* Score Urbain — affiché quand météo ou air est disponible */}
          <div className="md:col-span-2">
            {score.loading ? <CardLoader /> : score.error ? <CardError message={score.error} onRetry={score.refetch} /> : score.data && <UrbanScore data={score.data} />}
          </div>

          {/* Météo + Prévisions */}
          <div className="md:col-span-2">
            {weather.loading ? <CardLoader /> : weather.error ? <CardError message={weather.error} onRetry={weather.refetch} /> : weather.data && <WeatherCard data={weather.data} forecast={forecast.data} city={selectedCity} />}
          </div>

          {/* Qualité de l'air + Prédictions IA */}
          {air.loading ? <CardLoader /> : air.error ? <CardError message={air.error} onRetry={air.refetch} /> : air.data && <AirQualityCard data={air.data} />}
          <PredictionCard city={selectedCity} />

          {/* Carte interactive */}
          <div className="md:col-span-2">
            <MapSection city={selectedCity} aqi={air.data?.aqi || 1} />
          </div>

          {/* Événements à venir */}
          <div className="md:col-span-2">
            {events.loading ? <CardLoader /> : events.error ? <CardError message={events.error} onRetry={events.refetch} /> : events.data && <EventsList data={events.data} />}
          </div>

        </div>
      </main>
    </div>
  );
};

export default Index;