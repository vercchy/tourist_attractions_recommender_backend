from tensorflow.keras.models import load_model
import joblib
from app.config.config import MODEL_PATH, USER_ENCODER_PATH, ATTRACTION_ENCODER_PATH, EMBEDDING_MODEL_PATH, SCALER_PATH


def load_pretrained_model():
    model = load_model(MODEL_PATH)
    user_encoder = joblib.load(USER_ENCODER_PATH)
    attraction_encoder = joblib.load(ATTRACTION_ENCODER_PATH)
    embedding_model = load_model(EMBEDDING_MODEL_PATH)
    scaler = joblib.load(SCALER_PATH)

    return model, embedding_model, user_encoder, attraction_encoder, scaler
