"""Bereitgestellt: eigene DB auswählen, bevor tag7.db importiert wird."""
import os
from pathlib import Path

from dotenv import dotenv_values

ROOT = Path(__file__).resolve().parent.parent
settings = dotenv_values(ROOT / ".env.hausaufgabe")
password = settings.get("HW_DB_PASSWORD") or ""
if not password or password.startswith("CHANGE_"):
    raise RuntimeError("Zuerst .env.hausaufgabe mit Testpasswörtern anlegen.")

# Nur dieser Prozess wird geändert. Die normale .env bleibt unverändert.
os.environ.update({
    "MYSQL_HOST": "127.0.0.1",
    "MYSQL_PORT": settings.get("HW_DB_PORT") or "3309",
    "MYSQL_USER": "homework",
    "MYSQL_PASSWORD": password,
    "MYSQL_DATABASE": "hogwarts_hausaufgabe",
})
