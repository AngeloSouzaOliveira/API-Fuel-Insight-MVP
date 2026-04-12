import os
import pandas as pd
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

from app.ml.predictor import FuelPriceTierPredictor, FEATURES


DEFAULT_DATASET_URL = "https://raw.githubusercontent.com/AngeloSouzaOliveira/API-Fuel-Insight-MVP/refs/heads/main/data/all_countries_combined.csv"
DATASET_PATH = os.getenv("ML_DATASET_PATH", DEFAULT_DATASET_URL)
TARGET = "price_tier"


def test_model_is_loaded():
    predictor = FuelPriceTierPredictor()
    assert predictor.model is not None


def test_model_accuracy_threshold():
    predictor = FuelPriceTierPredictor()
    df = pd.read_csv(DATASET_PATH).dropna(subset=FEATURES + [TARGET]).copy()

    x_train, x_test, y_train, y_test = train_test_split(
        df[FEATURES], df[TARGET], test_size=0.2, random_state=42, stratify=df[TARGET]
    )
    y_pred = predictor.model.predict(x_test)
    acc = accuracy_score(y_test, y_pred)

    threshold = 0.70
    assert acc >= threshold, f"Accuracy {acc:.4f} below threshold {threshold:.2f}"
