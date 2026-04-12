from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt, jwt_required

from app.core import logger
from app.services.model_registry_service import ModelRegistryService


modelos_bp = Blueprint("modelos", __name__)


@modelos_bp.post("/api/modelos/registrar")
@jwt_required()
def registrar_modelo():
    claims = get_jwt()
    if claims.get("perfil") != "distribuicao":
        return jsonify({"success": False, "message": "Somente perfil distribuicao pode registrar modelo"}), 403

    payload = request.get_json() or {}
    required = ["version", "algorithm", "accuracy", "model_path"]
    missing = [k for k in required if k not in payload]
    if missing:
        return jsonify({"success": False, "message": f"Campos obrigatorios faltando: {missing}"}), 400
    try:
        row = ModelRegistryService.registrar_versao(
            version=str(payload["version"]),
            algorithm=str(payload["algorithm"]),
            accuracy=float(payload["accuracy"]),
            model_path=str(payload["model_path"]),
        )
        logger.info("modelo_registrado version=%s algoritmo=%s acc=%.4f", row.version, row.algorithm, row.accuracy)
        return jsonify({"success": True, "message": "Versao registrada", "data": {"version": row.version}}), 201
    except Exception as exc:
        return jsonify({"success": False, "message": str(exc)}), 400


@modelos_bp.post("/api/modelos/ativar")
@jwt_required()
def ativar_modelo():
    claims = get_jwt()
    if claims.get("perfil") != "distribuicao":
        return jsonify({"success": False, "message": "Somente perfil distribuicao pode ativar modelo"}), 403

    payload = request.get_json() or {}
    version = payload.get("version")
    min_accuracy = float(payload.get("min_accuracy", 0.8))
    if not version:
        return jsonify({"success": False, "message": "version eh obrigatorio"}), 400
    try:
        data = ModelRegistryService.ativar_com_rollback(version=version, min_accuracy=min_accuracy)
        logger.info("modelo_ativado version=%s rollback_de=%s", data.get("ativado"), data.get("rollback_de"))
        return jsonify({"success": True, "message": "Modelo ativado com sucesso", "data": data}), 200
    except Exception as exc:
        return jsonify({"success": False, "message": str(exc)}), 400


@modelos_bp.get("/api/modelos")
@jwt_required()
def listar_modelos():
    data = ModelRegistryService.listar()
    return jsonify({"success": True, "message": "Lista de modelos carregada", "data": data}), 200
