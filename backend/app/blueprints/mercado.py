from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from app.core import logger
from app.services.market_service import MarketService


mercado_bp = Blueprint("mercado", __name__)


@mercado_bp.get("/api/mercado/comparativo")
@jwt_required()
def mercado_comparativo():
    symbol = request.args.get("symbol", default="BZ=F", type=str)
    period_days = request.args.get("period_days", default=30, type=int)
    try:
        data = MarketService.compare_market(symbol=symbol, period_days=period_days)
        return jsonify({"success": True, "message": "Serie de mercado carregada", "data": data}), 200
    except ValueError as exc:
        return jsonify({"success": False, "message": str(exc)}), 400
    except Exception as exc:
        logger.exception("Falha no comparativo de mercado", exc_info=exc)
        return jsonify({"success": False, "message": "Fonte externa indisponível no momento. Tente outro ativo ou tente novamente em instantes."}), 502
