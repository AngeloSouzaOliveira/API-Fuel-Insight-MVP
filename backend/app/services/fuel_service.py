import csv
from pathlib import Path
from collections.abc import Callable
from sqlalchemy import func

from app.extensions import db
from app.models.fuel_prediction import FuelPrediction

DEFAULT_SEED_SCENARIOS = [
    {
        "year": 2024,
        "region": "Latin America",
        "subsidy_regime": "partial",
        "is_oil_producer": 1,
        "crude_oil_usd_per_barrel": 82.4,
        "tax_pct_of_pump_price": 22.0,
        "gasoline_real_2024usd": 1.15,
    },
    {
        "year": 2024,
        "region": "Europe",
        "subsidy_regime": "none",
        "is_oil_producer": 0,
        "crude_oil_usd_per_barrel": 82.4,
        "tax_pct_of_pump_price": 48.0,
        "gasoline_real_2024usd": 1.85,
    },
    {
        "year": 2024,
        "region": "North America",
        "subsidy_regime": "none",
        "is_oil_producer": 1,
        "crude_oil_usd_per_barrel": 82.4,
        "tax_pct_of_pump_price": 19.0,
        "gasoline_real_2024usd": 0.96,
    },
]


class FuelPredictionService:
    @staticmethod
    def country_options_from_dataset() -> list[str]:
        dataset_path = Path(__file__).resolve().parents[3] / "data" / "all_countries_combined.csv"
        if not dataset_path.exists():
            return []

        countries: set[str] = set()
        with dataset_path.open("r", encoding="utf-8", newline="") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                country = (row.get("country") or "").strip()
                if country:
                    countries.add(country)

        return sorted(countries)

    @staticmethod
    def save_prediction(payload: dict, predicted_tier: str) -> FuelPrediction:
        row = FuelPrediction(
            year=payload["year"],
            region=payload["region"],
            country=payload.get("country"),
            segmento=payload.get("segmento", "varejo"),
            subsidy_regime=payload["subsidy_regime"],
            is_oil_producer=payload["is_oil_producer"],
            crude_oil_usd_per_barrel=payload["crude_oil_usd_per_barrel"],
            tax_pct_of_pump_price=payload["tax_pct_of_pump_price"],
            gasoline_real_2024usd=payload["gasoline_real_2024usd"],
            predicted_price_tier=predicted_tier,
        )
        db.session.add(row)
        db.session.commit()
        return row

    @staticmethod
    def regional_summary(country: str | None = None, segmento: str | None = None) -> list[dict]:
        query = db.session.query(
            FuelPrediction.region.label("region"),
            FuelPrediction.predicted_price_tier.label("tier"),
            func.count(FuelPrediction.id).label("total"),
            func.avg(FuelPrediction.gasoline_real_2024usd).label("avg_real_2024usd"),
        )
        if country:
            query = query.filter(FuelPrediction.country == country)
        if segmento:
            query = query.filter(FuelPrediction.segmento == segmento)
        rows = (
            query
            .group_by(FuelPrediction.region, FuelPrediction.predicted_price_tier)
            .order_by(FuelPrediction.region.asc(), func.count(FuelPrediction.id).desc())
            .all()
        )
        return [
            {
                "region": row.region,
                "predicted_price_tier": row.tier,
                "predictions": int(row.total),
                "avg_gasoline_real_2024usd": float(row.avg_real_2024usd),
            }
            for row in rows
        ]

    @staticmethod
    def recent_predictions(limit: int = 20) -> list[FuelPrediction]:
        return (
            FuelPrediction.query.order_by(FuelPrediction.created_at.desc(), FuelPrediction.id.desc())
            .limit(limit)
            .all()
        )

    @staticmethod
    def top_risk_regions(limit: int = 5) -> list[dict]:
        high_risk_labels = ["Very High (>$1.60)", "High ($1.10–$1.60)"]
        rows = (
            db.session.query(
                FuelPrediction.region.label("region"),
                func.count(FuelPrediction.id).label("high_risk_predictions"),
                func.avg(FuelPrediction.gasoline_real_2024usd).label("avg_real_2024usd"),
            )
            .filter(FuelPrediction.predicted_price_tier.in_(high_risk_labels))
            .group_by(FuelPrediction.region)
            .order_by(func.count(FuelPrediction.id).desc())
            .limit(limit)
            .all()
        )
        return [
            {
                "region": row.region,
                "high_risk_predictions": int(row.high_risk_predictions),
                "avg_gasoline_real_2024usd": float(row.avg_real_2024usd),
            }
            for row in rows
        ]

    @staticmethod
    def seed_initial_predictions_if_empty(predict_fn: Callable[[dict], str], scenarios: list[dict] | None = None):
        if FuelPrediction.query.count() > 0:
            return {"seeded": False, "total": FuelPrediction.query.count()}

        effective_scenarios = scenarios if scenarios else DEFAULT_SEED_SCENARIOS
        for scenario in effective_scenarios:
            predicted_tier = str(predict_fn(scenario))
            FuelPredictionService.save_prediction(scenario, predicted_tier)
        return {"seeded": True, "total": FuelPrediction.query.count()}

    @staticmethod
    def dashboard_executivo() -> dict:
        total = FuelPrediction.query.count()
        high_risk_labels = ["Very High (>$1.60)", "High ($1.10–$1.60)"]
        high_risk = (
            db.session.query(func.count(FuelPrediction.id))
            .filter(FuelPrediction.predicted_price_tier.in_(high_risk_labels))
            .scalar()
        ) or 0

        top_region = (
            db.session.query(
                FuelPrediction.region.label("region"),
                func.count(FuelPrediction.id).label("qtd"),
                func.avg(FuelPrediction.gasoline_real_2024usd).label("media"),
            )
            .group_by(FuelPrediction.region)
            .order_by(func.count(FuelPrediction.id).desc())
            .first()
        )

        high_risk_pct = (float(high_risk) / float(total) * 100.0) if total else 0.0
        return {
            "total_predicoes": int(total),
            "predicoes_risco_alto": int(high_risk),
            "percentual_risco_alto": high_risk_pct,
            "acuracia_historica_estimada": 0.0,
            "volatilidade_mercado_ult_30d": None,
            "top_alertas": FuelPredictionService.alertas_ativos()[:3],
            "regiao_mais_ativa": (
                {
                    "regiao": top_region.region,
                    "predicoes": int(top_region.qtd),
                    "media_gasolina_real_2024usd": float(top_region.media),
                }
                if top_region
                else None
            ),
        }

    @staticmethod
    def alertas_ativos() -> list[dict]:
        top_risk = FuelPredictionService.top_risk_regions(limit=10)
        alertas = []
        for row in top_risk:
            if row["high_risk_predictions"] >= 2:
                alertas.append(
                    {
                        "tipo": "RISCO_ALTO_REGIAO",
                        "severidade": "alto",
                        "mensagem": f"Regiao {row['region']} com concentracao alta de previsoes caras.",
                        "regiao": row["region"],
                        "qtd_predicoes_risco_alto": row["high_risk_predictions"],
                    }
                )
        return alertas
