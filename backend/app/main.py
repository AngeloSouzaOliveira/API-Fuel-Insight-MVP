import json
import os
from pathlib import Path

from flask import Flask
from flask_cors import CORS
from flasgger import Swagger
from flask_jwt_extended import JWTManager

from app.blueprints import register_blueprints
from app.core import predictor
from app.extensions import bcrypt, db
from app.services.fuel_service import FuelPredictionService
from app.swagger import build_swagger_template


def _load_env() -> None:
    try:
        from dotenv import load_dotenv

        load_dotenv()
        return
    except ModuleNotFoundError:
        pass

    env_path = Path(__file__).resolve().parents[1] / ".env"
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


_load_env()


def _bool_env(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _load_seed_scenarios_from_env() -> list[dict] | None:
    raw = os.getenv("INITIAL_SEED_SCENARIOS", "").strip()
    if not raw:
        return None
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"INITIAL_SEED_SCENARIOS invalido: JSON malformado ({exc})") from exc
    if not isinstance(data, list) or not all(isinstance(item, dict) for item in data):
        raise ValueError("INITIAL_SEED_SCENARIOS deve ser um array JSON de objetos.")
    return data


def _executar_migracao_sqlite():
    stmts = [
        "ALTER TABLE fuel_predictions ADD COLUMN country VARCHAR(60)",
        "ALTER TABLE fuel_predictions ADD COLUMN segmento VARCHAR(30) DEFAULT 'varejo'",
    ]
    for stmt in stmts:
        try:
            db.session.execute(db.text(stmt))
            db.session.commit()
        except Exception:
            db.session.rollback()


app = Flask(__name__)
CORS(app)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///fuel_mvp.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "chave-super-secreta-mvp-fuel")
db.init_app(app)
bcrypt.init_app(app)
JWTManager(app)

with app.app_context():
    db.create_all()
    _executar_migracao_sqlite()
    if _bool_env("ENABLE_STARTUP_SEED", True):
        scenarios = _load_seed_scenarios_from_env()
        FuelPredictionService.seed_initial_predictions_if_empty(predictor.predict, scenarios=scenarios)

app.config["SWAGGER"] = {"title": "Fuel-Insight-MVP API", "uiversion": 3}
swagger = Swagger(app, template=build_swagger_template())
register_blueprints(app)


if __name__ == "__main__":
    debug_enabled = os.getenv("FLASK_ENV", "development").lower() == "development"
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "5000"))
    app.run(debug=debug_enabled, host=host, port=port)
