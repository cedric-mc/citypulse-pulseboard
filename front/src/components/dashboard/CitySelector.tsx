import { MapPin, Plus, X, ChevronDown } from "lucide-react";
import { useState, useEffect, useRef } from "react";

// Villes par défaut — non supprimables
const DEFAULT_CITIES = ["Paris", "Lyon", "Marseille", "Toulouse", "Nice", "Bordeaux"];
const STORAGE_KEY    = "customCities";

const loadCustomCities = (): string[] => {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    return stored ? JSON.parse(stored) : [];
  } catch {
    return [];
  }
};

interface CitySelectorProps {
  selectedCity: string;
  onCityChange: (cityId: string) => void;
}

const CitySelector = ({ selectedCity, onCityChange }: CitySelectorProps) => {
  const [customCity, setCustomCity]   = useState("");
  const [showInput, setShowInput]     = useState(false);
  const [showDropdown, setShowDropdown] = useState(false);
  const [customCities, setCustomCities] = useState<string[]>(loadCustomCities);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Persiste les villes custom en localStorage
  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(customCities));
  }, [customCities]);

  // Ferme le dropdown si clic en dehors
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setShowDropdown(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const allCities = [...DEFAULT_CITIES, ...customCities];

  const handleAddCity = () => {
    const trimmed     = customCity.trim();
    if (!trimmed) return;
    const capitalized = trimmed.charAt(0).toUpperCase() + trimmed.slice(1).toLowerCase();
    if (!allCities.includes(capitalized)) {
      setCustomCities(prev => [...prev, capitalized]);
    }
    onCityChange(capitalized);
    setCustomCity("");
    setShowInput(false);
    setShowDropdown(false);
  };

  // Supprime une ville — uniquement les villes custom
  // Les villes par défaut ne peuvent pas être supprimées
  const handleRemoveCity = (city: string, e: React.MouseEvent) => {
    e.stopPropagation(); // Évite de sélectionner la ville en cliquant sur ✕
    setCustomCities(prev => prev.filter(c => c !== city));
    // Si la ville supprimée était sélectionnée → revient sur Paris
    if (selectedCity === city) {
      onCityChange("Paris");
    }
  };

  const handleSelectCity = (city: string) => {
    onCityChange(city);
    setShowDropdown(false);
  };

  return (
    <div className="flex items-center gap-2">
      <MapPin className="h-4 w-4 text-primary" />

      {/* Dropdown custom — remplace le <select> HTML */}
      <div className="relative" ref={dropdownRef}>
        {/* Bouton déclencheur */}
        <button
          onClick={() => setShowDropdown(!showDropdown)}
          className="flex items-center gap-2 rounded-lg border border-border bg-card px-3 py-1.5 text-sm font-medium text-card-foreground focus:outline-none focus:ring-2 focus:ring-ring"
        >
          {selectedCity}
          <ChevronDown className={`h-4 w-4 text-muted-foreground transition-transform ${showDropdown ? "rotate-180" : ""}`} />
        </button>

        {/* Liste déroulante */}
        {showDropdown && (
          <div className="absolute right-0 top-full z-50 mt-1 w-48 rounded-lg border border-border bg-card shadow-lg">
            <div className="max-h-60 overflow-y-auto py-1">

              {/* Villes par défaut — non supprimables */}
              {DEFAULT_CITIES.map((c) => (
                <button
                  key={c}
                  onClick={() => handleSelectCity(c)}
                  className={`flex w-full items-center justify-between px-3 py-1.5 text-sm transition-colors hover:bg-secondary ${
                    selectedCity === c ? "bg-primary/10 text-primary font-semibold" : "text-card-foreground"
                  }`}
                >
                  {c}
                </button>
              ))}

              {/* Séparateur si villes custom présentes */}
              {customCities.length > 0 && (
                <div className="my-1 border-t border-border" />
              )}

              {/* Villes custom — supprimables via bouton ✕ */}
              {customCities.map((c) => (
                <div
                  key={c}
                  className={`flex w-full items-center justify-between px-3 py-1.5 text-sm transition-colors hover:bg-secondary ${
                    selectedCity === c ? "bg-primary/10 text-primary font-semibold" : "text-card-foreground"
                  }`}
                >
                  <button
                    onClick={() => handleSelectCity(c)}
                    className="flex-1 text-left"
                  >
                    {c}
                  </button>
                  {/* Bouton suppression — uniquement sur les villes custom */}
                  <button
                    onClick={(e) => handleRemoveCity(c, e)}
                    className="ml-2 rounded p-0.5 text-muted-foreground transition-colors hover:bg-destructive/10 hover:text-destructive"
                    title={`Supprimer ${c}`}
                  >
                    <X className="h-3 w-3" />
                  </button>
                </div>
              ))}

              {/* Séparateur + bouton ajouter ville */}
              <div className="my-1 border-t border-border" />
              <button
                onClick={() => {
                  setShowInput(true);
                  setShowDropdown(false);
                }}
                className="flex w-full items-center gap-2 px-3 py-1.5 text-sm text-primary transition-colors hover:bg-primary/10"
              >
                <Plus className="h-3.5 w-3.5" />
                Autre ville…
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Input ajout ville custom */}
      {showInput && (
        <div className="flex items-center gap-1">
          <input
            autoFocus
            value={customCity}
            onChange={(e) => setCustomCity(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleAddCity()}
            placeholder="Nom de la ville"
            className="w-32 rounded-lg border border-border bg-card px-2 py-1.5 text-sm text-card-foreground focus:outline-none focus:ring-2 focus:ring-ring"
          />
          <button
            onClick={handleAddCity}
            className="rounded-lg bg-primary p-1.5 text-primary-foreground hover:bg-primary/90"
          >
            <Plus className="h-3.5 w-3.5" />
          </button>
          <button
            onClick={() => setShowInput(false)}
            className="rounded-lg bg-secondary p-1.5 text-secondary-foreground hover:bg-secondary/80"
          >
            <X className="h-3.5 w-3.5" />
          </button>
        </div>
      )}
    </div>
  );
};

export default CitySelector;