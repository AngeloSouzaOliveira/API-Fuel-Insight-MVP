from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt, jwt_required
from marshmallow import ValidationError

from app.core import logger, predictor, request_schema, response_schema
from app.schemas.fuel import ALLOWED_REGIONS, ALLOWED_SEGMENTS, ALLOWED_SUBSIDIES
from app.services.fuel_service import FuelPredictionService
from app.services.market_service import MarketService
from app.services.model_registry_service import ModelRegistryService


combustivel_bp = Blueprint("combustivel", __name__)


@combustivel_bp.post("/api/combustivel/predizer")
@jwt_required()
def predict_fuel_tier():
    payload = request.get_json() or {}
    try:
        normalized = request_schema.load(payload)
    except ValidationError as exc:
        return jsonify({"success": False, "message": "Erro de validacao", "detalhes": exc.messages}), 400
    except Exception as exc:
        return jsonify({"success": False, "message": f"Payload invalido: {exc}"}), 400

    pred = predictor.predict(normalized)
    saved = FuelPredictionService.save_prediction(normalized, pred)
    claims = get_jwt()
    logger.info(
        "predicao_unitaria usuario=%s perfil=%s regiao=%s country=%s segmento=%s classe=%s",
        claims.get("username"),
        claims.get("perfil"),
        normalized.get("region"),
        normalized.get("country"),
        normalized.get("segmento"),
        pred,
    )
    return jsonify({"success": True, "message": "Predicao realizada com sucesso", "data": response_schema.dump(saved)}), 200


@combustivel_bp.post("/api/combustivel/predizer-lote")
@jwt_required()
def predict_fuel_tier_batch():
    payload = request.get_json() or {}
    items = payload.get("items")
    if not isinstance(items, list) or not items:
        return jsonify({"success": False, "message": "Payload precisa ter lista 'items' com pelo menos um item."}), 400

    results = []
    errors = []
    for idx, item in enumerate(items):
        try:
            normalized = request_schema.load(item)
            pred = predictor.predict(normalized)
            saved = FuelPredictionService.save_prediction(normalized, pred)
            results.append(response_schema.dump(saved))
        except ValidationError as exc:
            errors.append({"index": idx, "error": exc.messages})
        except Exception as exc:
            errors.append({"index": idx, "error": str(exc)})

    claims = get_jwt()
    logger.info(
        "predicao_lote usuario=%s perfil=%s total=%s sucesso=%s erros=%s",
        claims.get("username"),
        claims.get("perfil"),
        len(items),
        len(results),
        len(errors),
    )
    return jsonify({"success": True, "message": "Predicao em lote finalizada", "data": results, "errors": errors}), 200


@combustivel_bp.get("/api/combustivel/insights/regioes")
@jwt_required()
def fuel_region_insights():
    country = request.args.get("country", default=None, type=str)
    segmento = request.args.get("segmento", default=None, type=str)
    if segmento and segmento not in ALLOWED_SEGMENTS:
        return jsonify({"success": False, "message": "segmento invalido"}), 400
    data = FuelPredictionService.regional_summary(country=country, segmento=segmento)
    claims = get_jwt()
    logger.info(
        "insight_regioes usuario=%s perfil=%s country=%s segmento=%s linhas=%s",
        claims.get("username"),
        claims.get("perfil"),
        country,
        segmento,
        len(data),
    )
    return jsonify({"success": True, "message": "Resumo regional gerado", "data": data}), 200


@combustivel_bp.get("/api/combustivel/predicoes/recentes")
@jwt_required()
def recent_predictions():
    limit = request.args.get("limit", default=20, type=int)
    if limit < 1:
        return jsonify({"success": False, "message": "O parametro limit precisa ser >= 1"}), 400
    if limit > 200:
        return jsonify({"success": False, "message": "O parametro limit precisa ser <= 200"}), 400
    rows = FuelPredictionService.recent_predictions(limit=limit)
    return jsonify({"success": True, "message": "Historico recente carregado", "data": response_schema.dump(rows, many=True)}), 200


@combustivel_bp.get("/api/combustivel/insights/top-regioes-risco")
@jwt_required()
def top_risk_regions():
    limit = request.args.get("limit", default=5, type=int)
    if limit < 1:
        return jsonify({"success": False, "message": "O parametro limit precisa ser >= 1"}), 400
    if limit > 50:
        return jsonify({"success": False, "message": "O parametro limit precisa ser <= 50"}), 400
    data = FuelPredictionService.top_risk_regions(limit=limit)
    return jsonify({"success": True, "message": "Ranking de risco gerado", "data": data}), 200


@combustivel_bp.get("/api/combustivel/cenarios")
@jwt_required()
def fuel_cenarios():
    country_options = FuelPredictionService.country_options_from_dataset()
    return (
        jsonify(
            {
                "success": True,
                "message": "Cenarios carregados com sucesso",
                "data": {
                    "region_options": ALLOWED_REGIONS,
                    "country_options": country_options,
                    "subsidy_regime_options": ALLOWED_SUBSIDIES,
                    "is_oil_producer_options": [0, 1],
                    "ranges": {
                        "year": {"min": 1924, "max": 2035},
                        "crude_oil_usd_per_barrel": {"min": 0},
                        "tax_pct_of_pump_price": {"min": 0, "max": 100},
                        "gasoline_real_2024usd": {"min": 0},
                    },
                    "field_help": {
                        "year": "Ano do cenario economico que voce quer simular.",
                        "region": "Regiao usada pelo modelo para captar padrao geografico de preco.",
                        "subsidy_regime": "Tipo de subsidio no combustivel: none, partial ou heavy.",
                        "is_oil_producer": "1 para pais produtor de petroleo, 0 para nao produtor.",
                        "crude_oil_usd_per_barrel": "Preco internacional do barril (USD).",
                        "tax_pct_of_pump_price": "Percentual de imposto no valor final da bomba.",
                        "gasoline_real_2024usd": "Preco real da gasolina ajustado para dolar de 2024.",
                    },
                    "examples": [
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
                    ],
                },
            }
        ),
        200,
    )


@combustivel_bp.get("/api/combustivel/dashboard-executivo")
@jwt_required()
def dashboard_executivo():
    data = FuelPredictionService.dashboard_executivo()
    try:
        mercado = MarketService.compare_market(symbol="BZ=F", period_days=30)
        data["volatilidade_mercado_ult_30d"] = abs(float(mercado["variacao_pct"]))
    except Exception:
        data["volatilidade_mercado_ult_30d"] = None
    historico_modelo = ModelRegistryService.listar()
    if historico_modelo:
        data["acuracia_historica_estimada"] = float(historico_modelo[0]["accuracy"])
    claims = get_jwt()
    logger.info("dashboard_executivo usuario=%s perfil=%s", claims.get("username"), claims.get("perfil"))
    return jsonify({"success": True, "message": "Dashboard executivo gerado", "data": data}), 200


@combustivel_bp.get("/api/combustivel/alertas")
@jwt_required()
def alertas_ativos():
    data = FuelPredictionService.alertas_ativos()
    return jsonify({"success": True, "message": "Alertas processados", "data": data}), 200
