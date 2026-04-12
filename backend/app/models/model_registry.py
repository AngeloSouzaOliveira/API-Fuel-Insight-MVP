from datetime import UTC, datetime

from app.extensions import db


class ModelRegistry(db.Model):
    __tablename__ = "registro_modelos"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    version = db.Column(db.String(50), unique=True, nullable=False)
    algorithm = db.Column(db.String(50), nullable=False)
    accuracy = db.Column(db.Float, nullable=False)
    model_path = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, nullable=False, default=False)
    trained_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(UTC))
