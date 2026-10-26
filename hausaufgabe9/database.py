from hausaufgabe9 import config  # Vor tag7.db: eigene DB auswählen.
from sqlalchemy import text
from tag7.db import engine, SessionLocal


def check_database():
    if engine.url.database != "hogwarts_hausaufgabe":
        raise RuntimeError("Falsche Engine: Python-Prozess neu starten.")
    with engine.connect() as connection:
        if connection.scalar(text("SELECT DATABASE()")) != "hogwarts_hausaufgabe":
            raise RuntimeError("Nur die Hausaufgabendatenbank ist erlaubt.")
        revision = connection.scalar(text("SELECT version_num FROM alembic_version"))
        # Erst Ausgangsstand, dann die eigene kleine Migration.
        if revision not in {"0003", "hw9_owl"}:
            raise RuntimeError("Erwartet wird Revision 0003 oder hw9_owl.")
