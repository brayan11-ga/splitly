from sqlmodel import Session, select

from app.models import AuthSession, User


def find_user_by_email(session: Session, email: str) -> User | None:
    return session.exec(select(User).where(User.email == email)).first()


def find_session(session: Session, token_hash: str) -> AuthSession | None:
    return session.get(AuthSession, token_hash)
