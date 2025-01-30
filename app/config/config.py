import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

MODEL_PATH = BASE_DIR / "scripts" / "tourist_attractions_model.keras"
USER_ENCODER_PATH =  BASE_DIR / "scripts" / "user_encoder.pkl"
ATTRACTION_ENCODER_PATH = BASE_DIR / "scripts" / "attraction_encoder.pkl"
EMBEDDING_MODEL_PATH = BASE_DIR / "scripts" / "embedding_model.keras"
SCALER_PATH = BASE_DIR / "scripts" / "scaler.pkl"