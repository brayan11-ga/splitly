from sqlalchemy.exc import IntegrityError
from sqlmodel import Session


class NotFoundError(Exception):
    pass


class ConflictError(Exception):
    pass


def commit(session: Session) -> None:
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise ConflictError("La operación entra en conflicto con registros relacionados.") from None
