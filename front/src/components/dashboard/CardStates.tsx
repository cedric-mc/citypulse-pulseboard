import { motion } from "framer-motion";
import { Loader2, AlertCircle } from "lucide-react";

export const CardLoader = () => (
  <div className="dashboard-card flex min-h-[200px] items-center justify-center">
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex flex-col items-center gap-2 text-muted-foreground">
      <Loader2 className="h-6 w-6 animate-spin text-primary" />
      <span className="text-xs">Chargement…</span>
    </motion.div>
  </div>
);

export const CardError = ({ message, onRetry }: { message: string; onRetry?: () => void }) => (
  <div className="dashboard-card flex min-h-[200px] flex-col items-center justify-center gap-3">
    <AlertCircle className="h-6 w-6 text-destructive" />
    <p className="text-center text-sm text-muted-foreground">{message}</p>
    {onRetry && (
      <button onClick={onRetry} className="rounded-lg bg-primary px-3 py-1.5 text-xs font-medium text-primary-foreground transition-colors hover:bg-primary/90">
        Réessayer
      </button>
    )}
  </div>
);
