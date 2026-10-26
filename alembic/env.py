from alembic import context

# Vor tag7.db laden: dieses Repository verwendet nur die Hausaufgabendatenbank.
from hausaufgabe9 import config

from tag7.db import engine
from tag7.models import Base
import tag9.models  # users und access_tokens gehören zu denselben Metadaten.

target_metadata = Base.metadata

if engine.url.database != "hogwarts_hausaufgabe":
    raise RuntimeError("Nur die Hausaufgabendatenbank ist erlaubt.")


def run_migrations_offline():
    context.configure(
        url=engine.url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    with engine.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
