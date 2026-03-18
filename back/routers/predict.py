from fastapi import APIRouter, HTTPException
import pickle
import pandas as pd
import numpy as np
import os
from datetime import datetime
import requests

router = APIRouter()

# Charger le modèle au démarrage
model_path = os.path.join(os.path.dirname(__file__), '..', '..', 'ml', 'citypulse_model.pkl')
metadata_path = os.path.join(os.path.dirname(__file__), '..', '..', 'ml', 'citypulse_metadata.pkl')

try:
    with open(model_path, 'rb') as f:
        model = pickle.load(f)
    with open(metadata_path, 'rb') as f:
        metadata = pickle.load(f)
    model_loaded = True
    print("✅ Modèle chargé avec succès")
except Exception as e:
    model_loaded = False
    print(f"⚠️ Modèle non chargé: {e}")

# ⚠️ CORRECTION : suppression du "/api" pour éviter le double préfixe
@router.get("/predict/{city}")
async def predict_weather(city: str, hours: int = 6):
    """
    Prédit la température pour les prochaines heures
    - **city**: Nom de la ville
    - **hours**: Nombre d'heures à prédire (max 6)
    """
    if not model_loaded:
        raise HTTPException(status_code=500, detail="Modèle non disponible")
    
    if hours > 6:
        hours = 6
    
    try:
        # Clé API
        API_KEY = os.getenv('OPENWEATHER_API_KEY') or os.getenv('API_KEY') or 'ea71ace172bc2af269e7d9b238ba9c5e'
        
        # Appel API OpenWeatherMap
        url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units=metric"
        response = requests.get(url)
        
        if response.status_code != 200:
            raise HTTPException(status_code=404, detail=f"Ville '{city}' non trouvée")
        
        data = response.json()
        
        # Extraire les données
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
        
        # Préparer les prédictions
        predictions = []
        features_list = metadata['features']
        
        for i in range(hours):
            # Features temporelles
            hour = df.iloc[i + 4]['datetime'].hour
            day = df.iloc[i + 4]['datetime'].weekday()
            
            features = {
                'hour_sin': np.sin(2 * np.pi * hour / 24),
                'hour_cos': np.cos(2 * np.pi * hour / 24),
                'day_sin': np.sin(2 * np.pi * day / 7),
                'day_cos': np.cos(2 * np.pi * day / 7),
                'humidity': df.iloc[i + 4]['humidity'],
                'wind_speed': df.iloc[i + 4]['wind_speed'],
                'pressure': df.iloc[i + 4]['pressure'],
                'humidity_lag_1': df.iloc[i + 3]['humidity'],
                'wind_lag_1': df.iloc[i + 3]['wind_speed'],
                'temp_rolling_mean_6': df.iloc[i:i+6]['temperature'].mean()
            }
            
            # Créer DataFrame avec le bon ordre
            X_pred = pd.DataFrame([features])[features_list]
            
            # Prédire
            pred_temp = model.predict(X_pred)[0]
            
            predictions.append({
                'hour': i + 1,
                'datetime': df.iloc[i + 4]['datetime'].strftime('%Y-%m-%d %H:%M:%S'),
                'predicted_temperature': round(pred_temp, 1)
            })
        
        return {
            'city': city,
            'predictions': predictions,
            'confidence': metadata.get('confidence_score', 0.59),
            'model_mae': metadata.get('metrics', {}).get('test_mae', 2.06)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))