# Pipelines CityPulse

## Scripts

- collect_public_data.py:
  Collecte depuis les APIs publiques, normalise, charge la météo, la qualité de l'air et les évènements (weather/air/events).

- hourly_ingest.py:
  execution horaire continue (ou mode --once).

- simulate_48h.py:
  generation de donnees de test sur 48 heures (parametrable).

- normalization.py:
  fonctions de nettoyage, conversion et parsing.

## Execution

Depuis back:

python -m pipelines.collect_public_data
python -m pipelines.hourly_ingest --once
python -m pipelines.simulate_48h --hours 48
