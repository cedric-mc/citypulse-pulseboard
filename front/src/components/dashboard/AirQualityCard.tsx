import { motion, AnimatePresence } from "framer-motion";
import { Wind, AlertTriangle, Shield, Activity } from "lucide-react";
import type { AirQualityApiResponse } from "@/services/api";

interface AirQualityCardProps {
  data: AirQualityApiResponse;
}

const getAqiColor = (aqi: number) => {
  if (aqi <= 1) return "hsl(152, 69%, 45%)";
  if (aqi <= 2) return "hsl(38, 92%, 50%)";
  if (aqi <= 3) return "hsl(24, 95%, 53%)";
  if (aqi <= 4) return "hsl(0, 84%, 60%)";
  return "hsl(270, 50%, 60%)";
};

const getHealthMessage = (aqi: number) => {
  if (aqi <= 1) return { icon: Shield, message: "Excellent pour les activités extérieures 🌿" };
  if (aqi <= 2) return { icon: Activity, message: "Acceptable — personnes sensibles prudence ⚠️" };
  if (aqi <= 3) return { icon: AlertTriangle, message: "Limitez les efforts prolongés en extérieur" };
  if (aqi <= 4) return { icon: AlertTriangle, message: "Évitez le sport intensif en extérieur ⛔" };
  return { icon: AlertTriangle, message: "Danger — restez à l'intérieur 🚨" };
};

const AirQualityCard = ({ data }: AirQualityCardProps) => {
  const displayColor = getAqiColor(data.aqi);
  const gaugeWidth = Math.min((data.aqi / 5) * 100, 100);
  const health = getHealthMessage(data.aqi);
  const HealthIcon = health.icon;
  const isBad = data.aqi >= 4;

  const pollutants = [
    { label: "PM2.5", value: data.pollutants?.pm25 },
    { label: "NO₂", value: data.pollutants?.no2 },
    { label: "O₃", value: data.pollutants?.o3 },
    ...(data.pollutants?.co != null ? [{ label: "CO", value: data.pollutants.co }] : []),
  ];

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: 0.15 }}
      className="dashboard-card space-y-4"
    >
      <AnimatePresence>
        {isBad && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="overflow-hidden rounded-lg bg-destructive/10 border border-destructive/30 p-3 flex items-center gap-2"
          >
            <AlertTriangle className="h-4 w-4 text-destructive flex-shrink-0 animate-pulse" />
            <p className="text-xs font-medium text-destructive">Alerte pollution — Qualité de l'air dégradée</p>
          </motion.div>
        )}
      </AnimatePresence>

      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground">Qualité de l'air</h3>
        <Wind className="h-5 w-5 text-primary" />
      </div>

      <div className="flex items-end gap-3">
        <span className="text-4xl font-bold" style={{ color: displayColor }}>{data.aqi}</span>
        <span
          className="mb-1 inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold text-primary-foreground"
          style={{ backgroundColor: displayColor }}
        >
          {data.status}
        </span>
      </div>

      <div className="space-y-1">
        <div className="h-2.5 w-full overflow-hidden rounded-full bg-secondary">
          <motion.div
            className="h-full rounded-full"
            style={{ backgroundColor: displayColor }}
            initial={{ width: 0 }}
            animate={{ width: `${gaugeWidth}%` }}
            transition={{ duration: 0.8, ease: "easeOut" }}
          />
        </div>
        <div className="flex justify-between text-[10px] text-muted-foreground">
          <span>1 Bon</span><span>2</span><span>3</span><span>4</span><span>5 Danger</span>
        </div>
      </div>

      <div className="flex items-center gap-2 rounded-lg border border-border bg-muted/50 p-3">
        <HealthIcon className="h-4 w-4 flex-shrink-0" style={{ color: displayColor }} />
        <p className="text-xs font-medium text-foreground">{health.message}</p>
      </div>

      <div className={`grid gap-2 ${pollutants.length === 3 ? 'grid-cols-3' : 'grid-cols-4'}`}>
        {pollutants.map((p) => (
          <div key={p.label} className="rounded-lg bg-secondary/70 p-2.5 text-center">
            <p className="text-[10px] text-muted-foreground">{p.label}</p>
            <p className="text-sm font-bold text-foreground">{p.value != null ? Math.round(p.value * 10) / 10 : "—"}</p>
            <p className="text-[9px] text-muted-foreground">µg/m³</p>
          </div>
        ))}
      </div>
    </motion.div>
  );
};

export default AirQualityCard;
