from app.blueprints.auth import auth_bp
from app.blueprints.combustivel import combustivel_bp
from app.blueprints.mercado import mercado_bp
from app.blueprints.modelos import modelos_bp
from app.blueprints.sistema import sistema_bp


def register_blueprints(app):
    app.register_blueprint(sistema_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(combustivel_bp)
    app.register_blueprint(mercado_bp)
    app.register_blueprint(modelos_bp)
