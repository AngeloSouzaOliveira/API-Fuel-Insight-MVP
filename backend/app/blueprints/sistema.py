from flask import Blueprint, jsonify, redirect


sistema_bp = Blueprint("sistema", __name__)


@sistema_bp.get("/api/saude")
def health():
    return jsonify({"status": "ok", "mensagem": "API rodando normal"})


@sistema_bp.get("/")
def index():
    return redirect("/apidocs")
