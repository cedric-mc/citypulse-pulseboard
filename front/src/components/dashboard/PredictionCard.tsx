import { motion } from "framer-motion";
import { Brain, TrendingUp, Sparkles } from "lucide-react";

const PredictionCard = () => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: 0.35 }}
      className="dashboard-card relative overflow-hidden"
    >
      {/* Animated gradient background */}
      <div className="absolute inset-0 bg-gradient-to-br from-primary/5 via-transparent to-accent/5" />

      <div className="relative space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground">
            Prédictions IA
          </h3>
          <Brain className="h-5 w-5 text-primary" />
        </div>

        <div className="flex flex-col items-center gap-4 py-4">
          <motion.div
            animate={{ rotate: [0, 5, -5, 0] }}
            transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }}
            className="flex h-16 w-16 items-center justify-center rounded-2xl bg-primary/10"
          >
            <Sparkles className="h-8 w-8 text-primary" />
          </motion.div>

          <div className="text-center space-y-1">
            <p className="text-sm font-semibold text-foreground">Prédictions IA en cours de développement</p>
            <p className="text-xs text-muted-foreground">
              Bientôt : prévisions intelligentes basées sur les données urbaines
            </p>
          </div>

          {/* Placeholder slots */}
          <div className="grid w-full grid-cols-3 gap-2 mt-2">
            {[
              { label: "Valeur prédite", icon: TrendingUp },
              { label: "Tendance", icon: TrendingUp },
              { label: "Confiance", icon: Sparkles },
            ].map((slot) => (
              <div
                key={slot.label}
                className="flex flex-col items-center gap-1 rounded-lg border border-dashed border-border p-3"
              >
                <slot.icon className="h-4 w-4 text-muted-foreground/40" />
                <span className="text-[10px] text-muted-foreground/60">{slot.label}</span>
                <span className="text-sm font-bold text-muted-foreground/30">--</span>
              </div>
            ))}
          </div>
        </div>

        <div className="rounded-lg border border-dashed border-primary/20 bg-primary/5 p-2.5 text-center">
          <p className="text-[10px] text-primary/70">
            🔮 Endpoint prévu : /api/predict/{"{city}"}
          </p>
        </div>
      </div>
    </motion.div>
  );
};

export default PredictionCard;
