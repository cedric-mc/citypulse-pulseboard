from fastapi import APIRouter, HTTPException
import pickle
import pandas as pd
import numpy as np
import os
from datetime import datetime
import requests

router = APIRouter()

# Cache pour les modèles chargés
models_cache = {}
metadata_cache = {}

def load_model_for_city(city: str):
    """Charge le modèle et les métadonnées pour une ville donnée."""
    city_lower = city.lower()
    if city_lower in models_cache:
        return models_cache[city_lower], metadata_cache[city_lower]

    base_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'ml')
    
    if city_lower == "paris":
        model_path = os.path.join(base_dir, 'citypulse_model.pkl')
        meta_path = os.path.join(base_dir, 'citypulse_metadata.pkl')
    elif city_lower == "lille":
        model_path = os.path.join(base_dir, 'modele_lille_rf.pkl')
        meta_path = os.path.join(base_dir, 'metadata_lille_rf.pkl')
    else:
        # Par défaut, essayer Paris
        model_path = os.path.join(base_dir, 'citypulse_model.pkl')
        meta_path = os.path.join(base_dir, 'citypulse_metadata.pkl')

    try:
        with open(model_path, 'rb') as f:
            model = pickle.load(f)
        with open(meta_path, 'rb') as f:
            meta = pickle.load(f)

        # Uniformiser les métadonnées
        if 'metrics' in meta and 'test_mae' in meta['metrics']:
            meta['mae'] = meta['metrics']['test_mae']
            meta['confidence'] = meta.get('confidence_score', 0.59)
        elif 'mae' not in meta:
            meta['mae'] = 2.06
            meta['confidence'] = 0.59

        models_cache[city_lower] = model
        metadata_cache[city_lower] = meta
        print(f"✅ Modèle pour {city} chargé (MAE: {meta['mae']:.2f}°C)")
        return model, meta
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Impossible de charger le modèle pour {city}: {e}")

@router.get("/predict/{city}")
async def predict_weather(city: str, hours: int = 6):
    """
    Prédit la température pour les prochaines heures
    - **city**: Nom de la ville
    - **hours**: Nombre d'heures à prédire (max 6)
    """
    if hours > 6:
        hours = 6

    try:
        model, meta = load_model_for_city(city)
        features_list = meta['features']

        API_KEY = os.getenv('OPENWEATHER_API_KEY') or os.getenv('API_KEY') or 'ea71ace172bc2af269e7d9b238ba9c5e'

        url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units=metric"
        response = requests.get(url)

        if response.status_code != 200:
            raise HTTPException(status_code=404, detail=f"Ville '{city}' non trouvée")

        data = response.json()

        forecasts = []
        for item in data['list'][:hours + 4]:
            forecasts.append({
                'datetime': item['dt_txt'],
                'temperature': item['main']['temp'],
                'humidity': item['main']['humidity'],
                'wind_speed': item['wind']['speed'],
                'pressure': item['main']['pressure']
            })

        df = pd.DataFrame(forecasts)
        df['datetime'] = pd.to_datetime(df['datetime'])

        predictions = []

        for i in range(hours):
            pred_idx = i + 4
            current_dt = df.iloc[pred_idx]['datetime']
            hour = current_dt.hour
            day = current_dt.weekday()

            # Indices pour les moyennes mobiles (évite les indices négatifs)
            start_idx_3 = max(0, pred_idx - 3)
            start_idx_6 = max(0, pred_idx - 6)

            features_dict = {
                'hour_sin': np.sin(2 * np.pi * hour / 24),
                'hour_cos': np.cos(2 * np.pi * hour / 24),
                'day_sin': np.sin(2 * np.pi * day / 7),
                'day_cos': np.cos(2 * np.pi * day / 7),
                'humidity': df.iloc[pred_idx]['humidity'],
                'humidity_lag_1': df.iloc[pred_idx - 1]['humidity'],
                'humidity_lag_2': df.iloc[pred_idx - 2]['humidity'],
                'humidity_lag_3': df.iloc[pred_idx - 3]['humidity'],
                'humidity_lag_4': df.iloc[pred_idx - 4]['humidity'],
                'wind_speed': df.iloc[pred_idx]['wind_speed'],
                'wind_lag_1': df.iloc[pred_idx - 1]['wind_speed'],
                'wind_lag_2': df.iloc[pred_idx - 2]['wind_speed'],
                'wind_lag_3': df.iloc[pred_idx - 3]['wind_speed'],
                'wind_lag_4': df.iloc[pred_idx - 4]['wind_speed'],
                'pressure': df.iloc[pred_idx]['pressure'],
                'temp_lag_1': df.iloc[pred_idx - 1]['temperature'],
                'temp_lag_2': df.iloc[pred_idx - 2]['temperature'],
                'temp_lag_3': df.iloc[pred_idx - 3]['temperature'],
                'temp_lag_4': df.iloc[pred_idx - 4]['temperature'],
                'temp_rolling_mean_3': df.iloc[start_idx_3:pred_idx]['temperature'].mean(),
                'temp_rolling_mean_6': df.iloc[start_idx_6:pred_idx]['temperature'].mean(),
            }

            # Filtrer les features nécessaires
            X_dict = {k: features_dict[k] for k in features_list if k in features_dict}
            missing = set(features_list) - set(X_dict.keys())
            if missing:
                raise HTTPException(status_code=500, detail=f"Features manquantes pour {city}: {missing}")

            X_pred = pd.DataFrame([X_dict])[features_list]
            pred_temp = model.predict(X_pred)[0]

            predictions.append({
                'hour': i + 1,
                'datetime': df.iloc[pred_idx]['datetime'].strftime('%Y-%m-%d %H:%M:%S'),
                'predicted_temperature': round(pred_temp, 1)
            })

        return {
            'city': city,
            'predictions': predictions,
            'confidence': meta.get('confidence', 0.59),
            'model_mae': meta.get('mae', 2.06)
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))