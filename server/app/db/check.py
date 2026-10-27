"""Ejecutar con python -m app.db.check; solo lectura y solo splitly_dev local."""

from sqlalchemy import text

from app.config import get_settings
from app.db.session import get_database_url, get_engine


def main() -> int:
    settings = get_settings()
    if settings.database_url is None:
        print("Conexión no verificada: configura DATABASE_URL en server/.env.")
        return 1
    engine = None
    try:
        value = settings.database_url.get_secret_value()
        url = get_database_url(value)
        if url.host not in {"localhost", "127.0.0.1", "::1"} or url.database != "splitly_dev":
            print("Conexión rechazada: esta prueba solo permite PostgreSQL local / splitly_dev.")
            return 1
        engine = get_engine(value)
        with engine.connect() as connection:
            assert connection.execute(text("SELECT 1")).scalar_one() == 1
        print("Conexión PostgreSQL local correcta (SELECT 1). No se modificaron datos.")
        return 0
    except Exception:
        # No imprimir excepciones del driver: podrían contener datos de conexión.
        print("No se pudo verificar PostgreSQL local. Revisa servicio, base, usuario y contraseña.")
        return 1
    finally:
        if engine is not None:
            engine.dispose()


if __name__ == "__main__":
    raise SystemExit(main())
