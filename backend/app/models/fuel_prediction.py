from datetime import UTC, datetime

from app.extensions import db


class FuelPrediction(db.Model):
    __tablename__ = "fuel_predictions"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(UTC))

    year = db.Column(db.Integer, nullable=False)
    region = db.Column(db.String(60), nullable=False)
    country = db.Column(db.String(60), nullable=True)
    segmento = db.Column(db.String(30), nullable=False, default="varejo")
    subsidy_regime = db.Column(db.String(20), nullable=False)
    is_oil_producer = db.Column(db.Integer, nullable=False)
    crude_oil_usd_per_barrel = db.Column(db.Float, nullable=False)
    tax_pct_of_pump_price = db.Column(db.Float, nullable=False)
    gasoline_real_2024usd = db.Column(db.Float, nullable=False)

    predicted_price_tier = db.Column(db.String(40), nullable=False)
