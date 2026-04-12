from app.extensions import db
from app.models.model_registry import ModelRegistry


class ModelRegistryService:
    @staticmethod
    def registrar_versao(version: str, algorithm: str, accuracy: float, model_path: str) -> ModelRegistry:
        row = ModelRegistry(
            version=version,
            algorithm=algorithm,
            accuracy=accuracy,
            model_path=model_path,
            is_active=False,
        )
        db.session.add(row)
        db.session.commit()
        return row

    @staticmethod
    def ativar_com_rollback(version: str, min_accuracy: float = 0.8) -> dict:
        target = ModelRegistry.query.filter_by(version=version).first()
        if not target:
            raise ValueError("Versao nao encontrada.")
        if target.accuracy < min_accuracy:
            raise ValueError(f"Versao abaixo do limite de acuracia ({min_accuracy}).")

        prev_active = ModelRegistry.query.filter_by(is_active=True).first()
        if prev_active:
            prev_active.is_active = False
        target.is_active = True
        db.session.commit()
        return {
            "ativado": target.version,
            "rollback_de": prev_active.version if prev_active else None,
        }

    @staticmethod
    def listar() -> list[dict]:
        rows = ModelRegistry.query.order_by(ModelRegistry.trained_at.desc()).all()
        return [
            {
                "version": r.version,
                "algorithm": r.algorithm,
                "accuracy": r.accuracy,
                "model_path": r.model_path,
                "is_active": r.is_active,
                "trained_at": r.trained_at.isoformat(),
            }
            for r in rows
        ]
