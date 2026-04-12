from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token

from app.core import logger
from app.schemas.fuel import ALLOWED_SEGMENTS
from app.services.auth_service import AuthService


auth_bp = Blueprint("auth", __name__)


@auth_bp.post("/api/autenticacao/registrar")
def registrar_usuario():
    payload = request.get_json() or {}
    username = payload.get("username")
    password = payload.get("password")
    perfil = payload.get("perfil", "varejo")
    if not username or not password:
        return jsonify({"success": False, "message": "username e password sao obrigatorios"}), 400
    if perfil not in ALLOWED_SEGMENTS:
        return jsonify({"success": False, "message": "perfil invalido"}), 400
    try:
        user = AuthService.registrar(username=username, password=password, perfil=perfil)
        logger.info("novo_usuario_registrado username=%s perfil=%s", username, perfil)
        return (
            jsonify(
                {
                    "success": True,
                    "message": "Usuario registrado com sucesso",
                    "data": {"id": user.id, "username": user.username, "perfil": user.perfil},
                }
            ),
            201,
        )
    except ValueError as exc:
        return jsonify({"success": False, "message": str(exc)}), 400


@auth_bp.post("/api/autenticacao/login")
def login_usuario():
    payload = request.get_json() or {}
    username = payload.get("username")
    password = payload.get("password")
    if not username or not password:
        return jsonify({"success": False, "message": "username e password sao obrigatorios"}), 400
    try:
        user = AuthService.autenticar(username=username, password=password)
        logger.info("login_sucesso username=%s perfil=%s", user.username, user.perfil)
        token = create_access_token(identity=str(user.id), additional_claims={"perfil": user.perfil, "username": user.username})
        return (
            jsonify(
                {
                    "success": True,
                    "message": "Login realizado com sucesso",
                    "access_token": token,
                    "data": {"id": user.id, "username": user.username, "perfil": user.perfil},
                }
            ),
            200,
        )
    except ValueError as exc:
        return jsonify({"success": False, "message": str(exc)}), 401
