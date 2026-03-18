import { motion } from "framer-motion";
import { Cloud, Droplets, Thermometer, Wind, Eye } from "lucide-react";
import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { useNavigate } from "react-router-dom";
import type { WeatherApiResponse, ForecastApiResponse } from "@/services/api";

interface WeatherCardProps {
  data: WeatherApiResponse;
  forecast?: ForecastApiResponse | null;
  city: string;
}

const weatherIcons: Record<string, string> = {
  "01d": "☀️", "01n": "🌙", "02d": "⛅", "02n": "☁️",
  "03d": "☁️", "03n": "☁️", "04d": "☁️", "04n": "☁️",
  "09d": "🌧️", "09n": "🌧️", "10d": "🌦️", "10n": "🌧️",
  "11d": "⛈️", "11n": "⛈️", "13d": "❄️", "13n": "❄️",
  "50d": "🌫️", "50n": "🌫️",
};

const weatherBg: Record<string, string> = {
  "01d": "from-amber-400/10 to-orange-400/5",
  "01n": "from-indigo-500/10 to-slate-600/5",
  "02d": "from-sky-400/10 to-blue-300/5",
  "03d": "from-slate-300/10 to-gray-300/5",
  "04d": "from-slate-400/10 to-gray-400/5",
  "09d": "from-blue-500/10 to-slate-500/5",
  "10d": "from-blue-400/10 to-sky-400/5",
  "11d": "from-purple-500/10 to-slate-600/5",
  "13d": "from-cyan-200/10 to-blue-200/5",
  "50d": "from-gray-300/10 to-slate-300/5",
};

const getWeatherBg = (icon: string) => weatherBg[icon] || weatherBg[icon.replace("n", "d")] || "from-primary/5 to-primary/0";

const WeatherCard = ({ data, forecast, city }: WeatherCardProps) => {
  const navigate = useNavigate();
  const chartData = forecast?.forecasts.map((f) => ({
    hour: f.time.split(" ")[1]?.slice(0, 5) || f.time,
    temp: f.temperature,
  })) || [];

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: 0.1 }}
      className={`dashboard-card space-y-5 bg-gradient-to-br ${getWeatherBg(data.icon)}`}
    >
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground">Météo</h3>
        <button
          onClick={() => navigate(`/weather/${city}`)}
          className="flex items-center gap-1 rounded-lg px-2.5 py-1 text-xs font-medium text-primary transition-colors hover:bg-primary/10"
        >
          <Eye className="h-3.5 w-3.5" />
          Détails
        </button>
      </div>

      <div className="flex items-start justify-between">
        <div>
          <div className="flex items-center gap-3">
            <motion.span
              className="text-5xl"
              animate={{ scale: [1, 1.05, 1] }}
              transition={{ duration: 3, repeat: Infinity, ease: "easeInOut" }}
            >
              {weatherIcons[data.icon] || "🌤️"}
            </motion.span>
            <div>
              <p className="text-5xl font-bold text-foreground">{Math.round(data.temperature)}°</p>
              <p className="mt-1 text-sm capitalize text-muted-foreground">{data.description}</p>
            </div>
          </div>
        </div>
        <div className="space-y-2 text-right text-sm">
          <div className="flex items-center justify-end gap-1.5 text-muted-foreground">
            <Thermometer className="h-3.5 w-3.5" />
            <span>Ressenti {Math.round(data.feels_like)}°</span>
          </div>
          <div className="flex items-center justify-end gap-1.5 text-muted-foreground">
            <Droplets className="h-3.5 w-3.5" />
            <span>{data.humidity}%</span>
          </div>
          <div className="flex items-center justify-end gap-1.5 text-muted-foreground">
            <Wind className="h-3.5 w-3.5" />
            <span>{data.wind_speed} km/h</span>
          </div>
        </div>
      </div>

      {/* Mini forecast pills */}
      {forecast && forecast.forecasts.length > 0 && (
        <div className="flex gap-2 overflow-x-auto pb-1">
          {forecast.forecasts.slice(0, 6).map((f, i) => (
            <div key={i} className="flex flex-shrink-0 flex-col items-center gap-1 rounded-lg bg-secondary/60 px-3 py-2">
              <span className="text-[10px] text-muted-foreground">{f.time.split(" ")[1]?.slice(0, 5)}</span>
              <span className="text-sm">{weatherIcons[f.icon] || "🌤️"}</span>
              <span className="text-xs font-semibold text-foreground">{Math.round(f.temperature)}°</span>
            </div>
          ))}
        </div>
      )}

      {chartData.length > 0 && (
        <div className="h-36">
          <p className="mb-2 text-xs font-medium text-muted-foreground">Tendance 24h</p>
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={chartData}>
              <defs>
                <linearGradient id="tempGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="hsl(217, 91%, 60%)" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="hsl(217, 91%, 60%)" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" vertical={false} />
              <XAxis dataKey="hour" tick={{ fontSize: 10 }} stroke="hsl(var(--muted-foreground))" tickLine={false} axisLine={false} />
              <YAxis tick={{ fontSize: 10 }} stroke="hsl(var(--muted-foreground))" tickLine={false} axisLine={false} domain={['auto', 'auto']} unit="°" />
              <Tooltip
                contentStyle={{ backgroundColor: "hsl(var(--card))", border: "1px solid hsl(var(--border))", borderRadius: "8px", fontSize: "12px" }}
                formatter={(value: number) => [`${value}°C`, "Température"]}
              />
              <Area type="monotone" dataKey="temp" stroke="hsl(var(--primary))" strokeWidth={2} fill="url(#tempGradient)" />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      )}
    </motion.div>
  );
};

export default WeatherCard;
