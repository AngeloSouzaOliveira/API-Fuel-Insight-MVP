from app.extensions import db
from app.models.user import User


class AuthService:
    @staticmethod
    def registrar(username: str, password: str, perfil: str) -> User:
        if User.query.filter_by(username=username).first():
            raise ValueError("Usuario ja existe.")
        user = User(username=username, perfil=perfil)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return user

    @staticmethod
    def autenticar(username: str, password: str) -> User:
        user = User.query.filter_by(username=username).first()
        if not user or not user.check_password(password):
            raise ValueError("Credenciais invalidas.")
        return user
