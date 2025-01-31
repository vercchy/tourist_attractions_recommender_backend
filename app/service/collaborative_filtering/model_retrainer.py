from datetime import datetime
import numpy as np
import re
import tensorflow as tf
from sklearn.preprocessing import LabelEncoder, StandardScaler
from keras.models import Sequential
from keras.layers import Dense, Input, Dropout, Embedding, BatchNormalization,LeakyReLU
from tensorflow.keras.models import Model
from sklearn.model_selection import train_test_split
import joblib
import pandas as pd
from app.models.user_interaction import UserInteraction
from app.config.config import MODEL_PATH, USER_ENCODER_PATH, ATTRACTION_ENCODER_PATH, EMBEDDING_MODEL_PATH, SCALER_PATH


def load_data_from_db(db):
    # Query database for user interactions
    interactions = db.query(UserInteraction.user_id, UserInteraction.attraction_id, UserInteraction.rating).all()
    df = pd.DataFrame(interactions, columns=["user_id", "attraction_id", "rating"])
    return df

async def train_model(df, redis_client):
    await redis_client.set("model_currently_trained", 'true')

    df.rating = df.rating - 1

    X = df[["user_id", "attraction_id"]].copy()
    Y = df["rating"].values

    X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2, stratify=Y, random_state=42)

    user_encoder = LabelEncoder()
    attraction_encoder = LabelEncoder()

    X_train["user_id_encoded"] = user_encoder.fit_transform(X_train["user_id"])
    X_train["attraction_id_encoded"] = attraction_encoder.fit_transform(X_train["attraction_id"])

    X_test["user_id_encoded"] = user_encoder.transform(X_test["user_id"])
    X_test["attraction_id_encoded"] = attraction_encoder.transform(X_test["attraction_id"])

    num_users = X_train["user_id_encoded"].nunique()
    num_attractions = X_train["attraction_id_encoded"].nunique()
    embedding_dim = 100

    user_input = Input(shape=(1,), dtype="int32", name="user_id_input")
    attraction_input = Input(shape=(1,), dtype="int32", name="attraction_id_input")

    user_embedding = Embedding(input_dim=num_users, output_dim=embedding_dim, name="user_embedding")(user_input)
    attraction_embedding = Embedding(input_dim=num_attractions, output_dim=embedding_dim, name="attraction_embedding")(
        attraction_input)

    embedding_model = Model(inputs=[user_input, attraction_input], outputs=[user_embedding, attraction_embedding])

    user_ids_tensor_train = tf.constant(X_train["user_id_encoded"].values, dtype=tf.int32)
    attraction_ids_tensor_train = tf.constant(X_train["attraction_id_encoded"].values, dtype=tf.int32)

    user_embeddings_train, attraction_embeddings_train = embedding_model(
        [user_ids_tensor_train, attraction_ids_tensor_train])

    user_ids_tensor_test = tf.constant(X_test["user_id_encoded"].values, dtype=tf.int32)
    attraction_ids_tensor_test = tf.constant(X_test["attraction_id_encoded"].values, dtype=tf.int32)

    user_embeddings_test, attraction_embeddings_test = embedding_model(
        [user_ids_tensor_test, attraction_ids_tensor_test])

    X_train_features = np.hstack([
        user_embeddings_train.numpy().squeeze(),
        attraction_embeddings_train.numpy().squeeze()
    ])

    X_test_features = np.hstack([
        user_embeddings_test.numpy().squeeze(),
        attraction_embeddings_test.numpy().squeeze()
    ])

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train_features)
    X_test_scaled = scaler.transform(X_test_features)

    model = Sequential([
        Dense(256, activation="relu"),
        BatchNormalization(),
        Dropout(0.1),
        Dense(128, activation="relu"),
        BatchNormalization(),
        Dropout(0.1),
        Dense(64, activation="relu"),
        BatchNormalization(),
        Dropout(0.1),
        Dense(32, activation="relu"),
        Dense(5, activation="softmax")
    ])

    model.compile(optimizer="adam",
                  loss="sparse_categorical_crossentropy",
                  metrics=["accuracy"])

    history = model.fit(X_train_scaled, Y_train, batch_size=32, epochs=18, validation_split=0.2)

    loss, accuracy = model.evaluate(X_test_scaled, Y_test)
    print("Test Accuracy:", accuracy)

    await redis_client.set("collaborative_model_last_trained", datetime.utcnow().isoformat())
    await clear_user_predictions_after_gathering_new_data(redis_client)
    await redis_client.delete("model_currently_trained")

    model.save(MODEL_PATH)
    joblib.dump(user_encoder, USER_ENCODER_PATH)
    joblib.dump(attraction_encoder, ATTRACTION_ENCODER_PATH)
    embedding_model.save(EMBEDDING_MODEL_PATH)
    joblib.dump(scaler,SCALER_PATH)


async def gather_data_and_trigger_retraining(db, redis_client):
    data_frame = load_data_from_db(db)
    await train_model(data_frame, redis_client)
    print("Model retraining successfully completed!")



async def clear_user_predictions_after_gathering_new_data(redis_client):
    print("Clearing user predictions..")
    cursor = "0"
    pattern = "user:[0-9]*"

    while cursor != 0:
        cursor, keys = await redis_client.scan(cursor=cursor, match=pattern, count=100)
        valid_keys = [key for key in keys if re.match(r"user:\d+$", key.decode("utf-8"))]
        if valid_keys:
            await redis_client.delete(*valid_keys)

    print("User predictions cleared")