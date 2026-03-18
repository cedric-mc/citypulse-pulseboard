import { motion } from "framer-motion";
import { Brain, TrendingUp, TrendingDown, Minus, Sparkles, AlertCircle } from "lucide-react";
import { useFetch } from "@/hooks/useFetch";
import { getPredictions } from "@/services/api";

interface PredictionCardProps {
  city: string;
}

const PredictionCard = ({ city }: PredictionCardProps) => {
  const { data, loading, error } = useFetch(() => getPredictions(city, 6), [city]);

  const getTrend = () => {
    if (!data?.predictions || data.predictions.length < 2) return "stable";
    const first = data.predictions[0].predicted_temperature;
    const last = data.predictions[data.predictions.length - 1].predicted_temperature;
    const diff = last - first;
    if (diff > 1.5) return "hausse";
    if (diff < -1.5) return "baisse";
    return "stable";
  };

  const trend = getTrend();
  const TrendIcon = trend === "hausse" ? TrendingUp : trend === "baisse" ? TrendingDown : Minus;
  const trendColor = trend === "hausse" ? "text-orange-400" : trend === "baisse" ? "text-blue-400" : "text-green-400";
  const trendLabel = trend === "hausse" ? "📈 En hausse" : trend === "baisse" ? "📉 En baisse" : "➡️ Stable";

  const nextPrediction = data?.predictions?.[0];
  const confidencePct = data ? Math.round(data.confidence * 100) : null;
  const confidenceColor = confidencePct
    ? confidencePct >= 70 ? "text-green-400"
    : confidencePct >= 50 ? "text-yellow-400"
    : "text-red-400"
    : "";

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: 0.35 }}
      className="dashboard-card relative overflow-hidden"
    >
      <div className="absolute inset-0 bg-gradient-to-br from-primary/5 via-transparent to-accent/5" />

      <div className="relative space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground">
            Prédictions IA
          </h3>
          <Brain className="h-5 w-5 text-primary" />
        </div>

        {loading && (
          <div className="flex flex-col items-center gap-4 py-4">
            <motion.div
              animate={{ rotate: [0, 5, -5, 0] }}
              transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }}
              className="flex h-16 w-16 items-center justify-center rounded-2xl bg-primary/10"
            >
              <Sparkles className="h-8 w-8 text-primary animate-pulse" />
            </motion.div>
            <p className="text-xs text-muted-foreground">Chargement des prédictions...</p>
          </div>
        )}

        {error && !loading && (
          <div className="flex flex-col items-center gap-2 py-4">
            <AlertCircle className="h-8 w-8 text-red-400" />
            <p className="text-xs text-muted-foreground text-center">
              Prédictions temporairement indisponibles
            </p>
          </div>
        )}

        {data && !loading && !error && (
          <>
            <div className="grid w-full grid-cols-3 gap-2">
              <div className="flex flex-col items-center gap-1 rounded-lg border border-border bg-secondary/30 p-3">
                <TrendIcon className={`h-4 w-4 ${trendColor}`} />
                <span className="text-[10px] text-muted-foreground">Prochaine</span>
                <span className="text-sm font-bold text-foreground">
                  {nextPrediction ? `${nextPrediction.predicted_temperature}°C` : "--"}
                </span>
              </div>

              <div className="flex flex-col items-center gap-1 rounded-lg border border-border bg-secondary/30 p-3">
                <TrendIcon className={`h-4 w-4 ${trendColor}`} />
                <span className="text-[10px] text-muted-foreground">Tendance</span>
                <span className={`text-[11px] font-bold ${trendColor}`}>{trendLabel}</span>
              </div>

              <div className="flex flex-col items-center gap-1 rounded-lg border border-border bg-secondary/30 p-3">
                <Sparkles className={`h-4 w-4 ${confidenceColor}`} />
                <span className="text-[10px] text-muted-foreground">Confiance</span>
                <span className={`text-sm font-bold ${confidenceColor}`}>{confidencePct}%</span>
              </div>
            </div>

            <div className="space-y-1">
              <p className="text-[10px] text-muted-foreground uppercase tracking-wider">Prévisions sur 6h</p>
              <div className="grid grid-cols-3 gap-1">
                {data.predictions.map((pred) => (
                  <div key={pred.hour} className="flex items-center justify-between rounded-md bg-secondary/20 px-2 py-1">
                    <span className="text-[10px] text-muted-foreground">+{pred.hour}h</span>
                    <span className="text-[11px] font-semibold text-foreground">{pred.predicted_temperature}°C</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="rounded-lg border border-primary/20 bg-primary/5 p-2 text-center">
              <p className="text-[10px] text-primary/70">
                🤖 Modèle ML — Précision ±{data.model_mae}°C
              </p>
            </div>
          </>
        )}
      </div>
    </motion.div>
  );
};

export default PredictionCard;