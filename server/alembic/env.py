from alembic import context
from sqlmodel import SQLModel

import app.models  # noqa: F401 -- registra todas las tablas
from app.config import get_settings
from app.db.session import get_database_url, get_engine

target_metadata = SQLModel.metadata
settings = get_settings()
if settings.database_url is None:
    raise RuntimeError("Configura DATABASE_URL antes de ejecutar Alembic.")
database_url = settings.database_url.get_secret_value()


def include_object(obj, name, type_, reflected, compare_to):
    # Evita proponer borrados de tablas ajenas, p. ej. esquemas de Supabase.
    return not (type_ == "table" and reflected and compare_to is None)


if context.is_offline_mode():
    context.configure(
        url=get_database_url(database_url), target_metadata=target_metadata,
        literal_binds=True, dialect_opts={"paramstyle": "named"},
        include_object=include_object, compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()
else:
    engine = get_engine(database_url)
    try:
        with engine.connect() as connection:
            context.configure(
                connection=connection, target_metadata=target_metadata,
                include_object=include_object, compare_type=True,
            )
            with context.begin_transaction():
                context.run_migrations()
    finally:
        engine.dispose()
