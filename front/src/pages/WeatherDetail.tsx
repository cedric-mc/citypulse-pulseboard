import { useParams, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { ArrowLeft, Thermometer, Droplets, Wind, Cloud } from "lucide-react";
import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { useFetch } from "@/hooks/useFetch";
import { getWeather, getForecast } from "@/services/api";
import { CardLoader, CardError } from "@/components/dashboard/CardStates";

const weatherIcons: Record<string, string> = {
  "01d": "☀️", "01n": "🌙", "02d": "⛅", "02n": "☁️",
  "03d": "☁️", "03n": "☁️", "04d": "☁️", "04n": "☁️",
  "09d": "🌧️", "09n": "🌧️", "10d": "🌦️", "10n": "🌧️",
  "11d": "⛈️", "11n": "⛈️", "13d": "❄️", "13n": "❄️",
  "50d": "🌫️", "50n": "🌫️",
};

const WeatherDetail = () => {
  const { city } = useParams<{ city: string }>();
  const navigate = useNavigate();
  const cityName = city || "Paris";

  const weather = useFetch(() => getWeather(cityName), [cityName]);
  const forecast = useFetch(() => getForecast(cityName), [cityName]);

  const chartData = forecast.data?.forecasts.map((f) => ({
    hour: f.time.split(" ")[1]?.slice(0, 5) || f.time,
    temp: f.temperature,
    humidity: f.humidity,
    feelsLike: f.feels_like,
  })) || [];

  return (
    <div className="min-h-screen bg-background">
      <header className="sticky top-0 z-50 border-b border-border bg-card/80 backdrop-blur-md">
        <div className="container flex h-14 items-center gap-3">
          <button onClick={() => navigate("/")} className="rounded-lg p-2 text-muted-foreground hover:bg-secondary hover:text-foreground transition-colors">
            <ArrowLeft className="h-5 w-5" />
          </button>
          <Cloud className="h-5 w-5 text-primary" />
          <span className="text-lg font-bold text-foreground">Météo — {cityName}</span>
        </div>
      </header>

      <main className="container py-6 space-y-6">
        {weather.loading ? <CardLoader /> : weather.error ? <CardError message={weather.error} onRetry={weather.refetch} /> : weather.data && (
          <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} className="dashboard-card">
            <div className="flex items-start gap-6 flex-wrap">
              <div className="flex items-center gap-4">
                <span className="text-7xl">{weatherIcons[weather.data.icon] || "🌤️"}</span>
                <div>
                  <p className="text-6xl font-bold text-foreground">{Math.round(weather.data.temperature)}°C</p>
                  <p className="text-lg capitalize text-muted-foreground mt-1">{weather.data.description}</p>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 flex-1 min-w-[200px]">
                {[
                  { icon: Thermometer, label: "Ressenti", value: `${Math.round(weather.data.feels_like)}°C` },
                  { icon: Droplets, label: "Humidité", value: `${weather.data.humidity}%` },
                  { icon: Wind, label: "Vent", value: `${weather.data.wind_speed} km/h` },
                ].map((stat) => (
                  <div key={stat.label} className="rounded-xl bg-secondary/50 p-4">
                    <div className="flex items-center gap-2 text-muted-foreground mb-1">
                      <stat.icon className="h-4 w-4" />
                      <span className="text-xs">{stat.label}</span>
                    </div>
                    <p className="text-xl font-bold text-foreground">{stat.value}</p>
                  </div>
                ))}
              </div>
            </div>
          </motion.div>
        )}

        {/* Forecast cards */}
        {forecast.data && forecast.data.forecasts.length > 0 && (
          <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }} className="dashboard-card space-y-4">
            <h3 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground">Prévisions détaillées</h3>
            <div className="flex gap-3 overflow-x-auto pb-2">
              {forecast.data.forecasts.map((f, i) => (
                <div key={i} className="flex flex-shrink-0 flex-col items-center gap-2 rounded-xl bg-secondary/50 px-4 py-3 min-w-[90px]">
                  <span className="text-xs text-muted-foreground">{f.time.split(" ")[1]?.slice(0, 5)}</span>
                  <span className="text-2xl">{weatherIcons[f.icon] || "🌤️"}</span>
                  <span className="text-lg font-bold text-foreground">{Math.round(f.temperature)}°</span>
                  <span className="text-[10px] text-muted-foreground capitalize">{f.description}</span>
                  <div className="flex items-center gap-1 text-[10px] text-muted-foreground">
                    <Droplets className="h-2.5 w-2.5" />
                    {f.humidity}%
                  </div>
                </div>
              ))}
            </div>
          </motion.div>
        )}

        {/* Chart */}
        {chartData.length > 0 && (
          <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }} className="dashboard-card space-y-4">
            <h3 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground">Graphique température 24h</h3>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={chartData}>
                  <defs>
                    <linearGradient id="tempGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="hsl(217, 91%, 60%)" stopOpacity={0.3} />
                      <stop offset="95%" stopColor="hsl(217, 91%, 60%)" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" vertical={false} />
                  <XAxis dataKey="hour" tick={{ fontSize: 11 }} stroke="hsl(var(--muted-foreground))" tickLine={false} axisLine={false} />
                  <YAxis tick={{ fontSize: 11 }} stroke="hsl(var(--muted-foreground))" tickLine={false} axisLine={false} unit="°" domain={["auto", "auto"]} />
                  <Tooltip
                    contentStyle={{ backgroundColor: "hsl(var(--card))", border: "1px solid hsl(var(--border))", borderRadius: "8px", fontSize: "12px" }}
                    formatter={(value: number, name: string) => {
                      const labels: Record<string, string> = { temp: "Température", humidity: "Humidité", feelsLike: "Ressenti" };
                      return [`${value}${name === "humidity" ? "%" : "°C"}`, labels[name] || name];
                    }}
                  />
                  <Area type="monotone" dataKey="temp" stroke="hsl(var(--primary))" strokeWidth={2} fill="url(#tempGrad)" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </motion.div>
        )}
      </main>
    </div>
  );
};

export default WeatherDetail;
