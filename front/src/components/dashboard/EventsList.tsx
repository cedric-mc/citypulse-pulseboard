import { motion } from "framer-motion";
import { Calendar, MapPin, ExternalLink, Tag, ChevronDown } from "lucide-react";
import { useState } from "react";
import type { EventsApiResponse } from "@/services/api";

interface EventsListProps {
  data: EventsApiResponse;
}

const categoryColors: Record<string, string> = {
  "événement": "bg-primary/15 text-primary",
  conférence: "bg-primary/15 text-primary",
  visite: "bg-success/15 text-success",
  concert: "bg-warning/15 text-warning",
  spectacle: "bg-destructive/15 text-destructive",
  exposition: "bg-accent/15 text-accent-foreground",
};

const getCategoryStyle = (cat: string) => {
  const key = cat.toLowerCase().replace(/^:/, "");
  return categoryColors[key] || "bg-secondary text-secondary-foreground";
};

const formatDate = (dateStr: string, timeStr?: string) => {
  try {
    const d = new Date(dateStr);
    const opts: Intl.DateTimeFormatOptions = { day: "numeric", month: "short" };
    let result = d.toLocaleDateString("fr-FR", opts);
    if (timeStr) {
      result += ` ${timeStr.slice(0, 5)}`;
    }
    return result;
  } catch {
    return dateStr;
  }
};

const EventsList = ({ data }: EventsListProps) => {
  const [showAll, setShowAll] = useState(false);
  const events = data;
  const visibleEvents = showAll ? events : events.slice(0, 4);

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: 0.3 }}
      className="dashboard-card space-y-4"
    >
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground">
          Événements à venir
        </h3>
        <span className="rounded-full bg-primary/10 px-2.5 py-0.5 text-xs font-semibold text-primary">
          {events.length} événement{events.length !== 1 ? "s" : ""}
        </span>
      </div>

      {events.length === 0 ? (
        <div className="flex flex-col items-center gap-2 py-10">
          <Calendar className="h-10 w-10 text-muted-foreground/40" />
          <p className="text-sm text-muted-foreground">Aucun événement à venir</p>
        </div>
      ) : (
        <>
          <div className="grid gap-3 sm:grid-cols-2">
            {visibleEvents.map((event, i) => (
              <motion.div
                key={`${event.title}-${i}`}
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.05 * i }}
                className="group relative flex flex-col gap-2.5 rounded-xl border border-border bg-card p-4 transition-all duration-200 hover:-translate-y-0.5 hover:border-primary/30 hover:shadow-lg"
              >
                <div className="flex items-start justify-between gap-2">
                  <p className="text-sm font-semibold text-foreground line-clamp-2 group-hover:text-primary transition-colors">
                    {event.title}
                  </p>
                  {(event.url || event.link) && (
                    <a href={event.url || event.link} target="_blank" rel="noopener noreferrer">
                      <ExternalLink className="h-3.5 w-3.5 flex-shrink-0 text-muted-foreground opacity-0 transition-opacity group-hover:opacity-100" />
                    </a>
                  )}
                </div>

                {event.description && (
                  <p className="text-xs text-muted-foreground line-clamp-2">{event.description}</p>
                )}

                <div className="mt-auto flex flex-wrap items-center gap-2">
                  {event.category && (
                    <span className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-[10px] font-semibold ${getCategoryStyle(event.category)}`}>
                      <Tag className="h-2.5 w-2.5" />
                      {event.category}
                    </span>
                  )}
                </div>

                <div className="flex flex-wrap items-center gap-x-3 gap-y-1 text-[11px] text-muted-foreground">
                  {(event.date || event.date_start) && (
                    <span className="flex items-center gap-1">
                      <Calendar className="h-3 w-3" />
                      {formatDate(event.date || event.date_start!, event.time)}
                    </span>
                  )}
                  {(event.location || event.location_name) && (
                    <span className="flex items-center gap-1">
                      <MapPin className="h-3 w-3" />
                      {event.location || event.location_name}
                    </span>
                  )}
                </div>
              </motion.div>
            ))}
          </div>

          {events.length > 4 && (
            <button
              onClick={() => setShowAll(!showAll)}
              className="mx-auto flex items-center gap-1 rounded-lg px-4 py-2 text-xs font-medium text-primary transition-colors hover:bg-primary/10"
            >
              {showAll ? "Voir moins" : `Voir les ${events.length} événements`}
              <ChevronDown className={`h-3.5 w-3.5 transition-transform ${showAll ? "rotate-180" : ""}`} />
            </button>
          )}
        </>
      )}
    </motion.div>
  );
};

export default EventsList;
