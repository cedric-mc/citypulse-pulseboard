import { motion, AnimatePresence } from "framer-motion";
import { Info, TrendingUp, Cloud, Wind as WindIcon, Calendar } from "lucide-react";
import { useState } from "react";
import type { UrbanScoreApiResponse } from "@/services/api";

interface UrbanScoreProps {
  data: UrbanScoreApiResponse;
}

const getScoreColor = (score: number) => {
  if (score >= 80) return "text-success";
  if (score >= 50) return "text-warning";
  return "text-destructive";
};

const getScoreBg = (score: number) => {
  if (score >= 80) return "bg-success";
  if (score >= 50) return "bg-warning";
  return "bg-destructive";
};

const getScoreRing = (score: number) => {
  if (score >= 80) return "hsl(152, 69%, 45%)";
  if (score >= 50) return "hsl(38, 92%, 50%)";
  return "hsl(0, 84%, 60%)";
};

const getScoreLabel = (score: number) => {
  if (score >= 80) return "Excellent";
  if (score >= 60) return "Bon";
  if (score >= 50) return "Correct";
  return "Mauvais";
};

const getScoreDescription = (score: number) => {
  if (score >= 80) return "Conditions urbaines idéales pour sortir et profiter de la ville.";
  if (score >= 60) return "Bonnes conditions générales avec quelques points à surveiller.";
  if (score >= 50) return "Conditions acceptables, restez informé des évolutions.";
  return "Conditions dégradées, prudence recommandée.";
};

const criteriaConfig = [
  { key: "weather_score" as const, label: "Météo", icon: Cloud, desc: "Température, ciel, vent", weight: "40%" },
  { key: "air_score" as const, label: "Qualité de l'air", icon: WindIcon, desc: "AQI et polluants", weight: "35%" },
  { key: "events_score" as const, label: "Événements", icon: Calendar, desc: "Activités disponibles", weight: "25%" },
];

const UrbanScore = ({ data }: UrbanScoreProps) => {
  const [showInfo, setShowInfo] = useState(false);
  const score = Math.round(data.score);
  const circumference = 2 * Math.PI * 54;
  const strokeDashoffset = circumference - (score / 100) * circumference;

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="dashboard-card"
    >
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground">
          Score Urbain
        </h3>
        <button
          onClick={() => setShowInfo(!showInfo)}
          className="flex items-center gap-1 rounded-full px-2 py-1 text-xs text-muted-foreground transition-colors hover:bg-secondary hover:text-foreground"
        >
          <Info className="h-3.5 w-3.5" />
          <span className="hidden sm:inline">Comment ça marche ?</span>
        </button>
      </div>

      <AnimatePresence>
        {showInfo && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="overflow-hidden mb-4"
          >
            <div className="rounded-lg border border-border bg-muted/50 p-4 space-y-2">
              <p className="text-xs font-semibold text-foreground">📊 Qu'est-ce que le Score Urbain ?</p>
              <p className="text-xs text-muted-foreground leading-relaxed">
                Le score urbain évalue en temps réel la qualité de vie dans votre ville sur une échelle de 0 à 100.
                Il combine trois critères pondérés : la météo (40%), la qualité de l'air (35%),
                et les événements culturels (25%).
              </p>
              <p className="text-xs text-muted-foreground">Plus le score est élevé, meilleures sont les conditions pour profiter de la ville !</p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      <div className="flex flex-col items-center gap-4 md:flex-row md:gap-8">
        {/* Score circle */}
        <div className="relative flex flex-shrink-0 items-center justify-center">
          <svg width="160" height="160" viewBox="0 0 120 120">
            <circle cx="60" cy="60" r="54" fill="none" stroke="hsl(var(--border))" strokeWidth="8" />
            <motion.circle
              cx="60" cy="60" r="54" fill="none"
              stroke={getScoreRing(score)}
              strokeWidth="8"
              strokeLinecap="round"
              strokeDasharray={circumference}
              initial={{ strokeDashoffset: circumference }}
              animate={{ strokeDashoffset }}
              transition={{ duration: 1.2, ease: "easeOut" }}
              transform="rotate(-90 60 60)"
            />
          </svg>
          <div className="absolute flex flex-col items-center">
            <motion.span
              className={`text-4xl font-bold ${getScoreColor(score)}`}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.5 }}
            >
              {score}
            </motion.span>
            <span className="text-xs text-muted-foreground">/100</span>
          </div>
        </div>

        {/* Right side details */}
        <div className="flex-1 space-y-3 w-full">
          <div className="flex items-center gap-2">
            <span className={`inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-semibold ${getScoreBg(score)} text-primary-foreground`}>
              <TrendingUp className="h-3 w-3" />
              {getScoreLabel(score)}
            </span>
          </div>
          <p className="text-xs text-muted-foreground">{getScoreDescription(score)}</p>

          {/* Criteria breakdown */}
          <div className="space-y-2.5">
            {criteriaConfig.map((c) => {
              const value = data.details?.[c.key] ?? 0;
              return (
                <div key={c.key} className="space-y-1">
                  <div className="flex items-center justify-between text-xs">
                    <span className="flex items-center gap-1.5 text-muted-foreground">
                      <c.icon className="h-3 w-3" />
                      {c.label}
                      <span className="text-[10px] opacity-60">({c.weight})</span>
                    </span>
                    <span className={`font-semibold ${getScoreColor(value)}`}>{Math.round(value)}/100</span>
                  </div>
                  <div className="h-1.5 w-full overflow-hidden rounded-full bg-secondary">
                    <motion.div
                      className="h-full rounded-full"
                      style={{ backgroundColor: getScoreRing(value) }}
                      initial={{ width: 0 }}
                      animate={{ width: `${value}%` }}
                      transition={{ duration: 0.8, ease: "easeOut", delay: 0.3 }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </motion.div>
  );
};

export default UrbanScore;
