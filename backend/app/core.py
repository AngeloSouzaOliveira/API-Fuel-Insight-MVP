import logging

from app.ml.predictor import FuelPriceTierPredictor
from app.schemas.fuel import FuelPredictionRequestSchema, FuelPredictionResponseSchema


predictor = FuelPriceTierPredictor()
request_schema = FuelPredictionRequestSchema()
response_schema = FuelPredictionResponseSchema()

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("fuel_api")
