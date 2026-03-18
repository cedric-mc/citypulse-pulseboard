from .weather import router as weather_router
from .air import router as air_router
from .events import router as events_router
from .score import router as score_router
from .predict import router as predict_router

# Cette ligne rend tous les routers disponibles
__all__ = [
    "weather_router",
    "air_router", 
    "events_router",
    "score_router",
    "predict_router"
]