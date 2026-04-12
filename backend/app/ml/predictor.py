import os
import joblib
import pandas as pd


FEATURES = [
    "year",
    "region",
    "subsidy_regime",
    "is_oil_producer",
    "crude_oil_usd_per_barrel",
    "tax_pct_of_pump_price",
    "gasoline_real_2024usd",
]


class FuelPriceTierPredictor:
    def __init__(self):
        model_path = os.path.join(os.path.dirname(__file__), "fuel_price_tier_model.pkl")
        self.model = joblib.load(model_path)

    def predict(self, payload: dict) -> str:
        missing = [k for k in FEATURES if k not in payload]
        if missing:
            raise ValueError(f"Missing required features: {missing}")
        row = pd.DataFrame([{k: payload[k] for k in FEATURES}])
        pred = self.model.predict(row)
        return str(pred[0])
