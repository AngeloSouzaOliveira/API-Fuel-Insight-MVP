from marshmallow import Schema, ValidationError, fields, validate


ALLOWED_SUBSIDIES = ["none", "partial", "heavy"]
ALLOWED_SEGMENTS = ["varejo", "logistica", "distribuicao"]
ALLOWED_REGIONS = [
    "Latin America",
    "North America",
    "Europe",
    "Asia",
    "Asia Pacific",
    "Middle East",
    "Africa",
    "Eurasia",
    "Europe/Asia",
]


def validate_binary(value):
    if value not in (0, 1):
        raise ValidationError("is_oil_producer must be 0 or 1.")


class FuelPredictionRequestSchema(Schema):
    year = fields.Int(required=True, validate=validate.Range(min=1924, max=2035))
    region = fields.Str(required=True, validate=validate.OneOf(ALLOWED_REGIONS))
    country = fields.Str(required=False, allow_none=True, validate=validate.Length(min=2, max=60))
    segmento = fields.Str(required=False, validate=validate.OneOf(ALLOWED_SEGMENTS), load_default="varejo")
    subsidy_regime = fields.Str(required=True, validate=validate.OneOf(ALLOWED_SUBSIDIES))
    is_oil_producer = fields.Int(required=True, validate=validate_binary)
    crude_oil_usd_per_barrel = fields.Float(required=True, validate=validate.Range(min=0))
    tax_pct_of_pump_price = fields.Float(required=True, validate=validate.Range(min=0, max=100))
    gasoline_real_2024usd = fields.Float(required=True, validate=validate.Range(min=0))


class FuelPredictionResponseSchema(FuelPredictionRequestSchema):
    id = fields.Int(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    predicted_price_tier = fields.Str(dump_only=True)
