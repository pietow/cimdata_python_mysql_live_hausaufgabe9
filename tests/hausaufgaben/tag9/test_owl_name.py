"""Vorgegebene Tests zu Aufgabe 3. Diese Datei nicht verändern."""
from pathlib import Path

from alembic.config import Config
from alembic.script import ScriptDirectory
from sqlalchemy import String, text
from tag7.models import Student


def test_model_column_definition():
    columns = Student.__table__.columns
    assert "owl_name" in columns, "Student braucht die Spalte owl_name."
    column = columns["owl_name"]
    assert isinstance(column.type, String)
    assert column.type.length == 50
    assert column.nullable is True


def test_real_column_and_revision(db_factory):
    with db_factory() as db:
        column = db.execute(text("SHOW COLUMNS FROM students LIKE 'owl_name'")).mappings().one_or_none()
        assert column is not None, "Die Migration muss owl_name in MySQL anlegen."
        assert column["Type"].lower() == "varchar(50)"
        assert column["Null"] == "YES"
        assert db.scalar(text("SELECT version_num FROM alembic_version")) == "hw9_owl"


def test_migration_follows_0003():
    root = next(parent for parent in Path(__file__).resolve().parents
                if (parent / "alembic.ini").is_file())
    scripts = ScriptDirectory.from_config(Config(str(root / "alembic.ini")))
    assert scripts.get_heads() == ["hw9_owl"], "Die eigene Revision hw9_owl fehlt oder es gibt mehrere Köpfe."
    assert scripts.get_revision("hw9_owl").down_revision == "0003"


def test_owl_name_is_persisted(db_factory, sample):
    student_id = sample["harry_id"]
    with db_factory() as db:
        old_value = db.get(Student, student_id).owl_name
    try:
        with db_factory() as db:
            db.get(Student, student_id).owl_name = "Hedwig"
            db.commit()
        # Eine neue Session prüft den tatsächlich gespeicherten Wert.
        with db_factory() as db:
            assert db.get(Student, student_id).owl_name == "Hedwig"
    finally:
        # Auch nach einem Assert-Fehler mit einer frischen Session aufräumen.
        with db_factory() as db:
            db.get(Student, student_id).owl_name = old_value
            db.commit()


def test_owl_name_may_be_none(db_factory, sample):
    student_id = sample["harry_id"]
    with db_factory() as db:
        old_value = db.get(Student, student_id).owl_name
    try:
        with db_factory() as db:
            db.get(Student, student_id).owl_name = "Hedwig"
            db.commit()
        with db_factory() as db:
            db.get(Student, student_id).owl_name = None
            db.commit()
        with db_factory() as db:
            assert db.get(Student, student_id).owl_name is None
    finally:
        with db_factory() as db:
            db.get(Student, student_id).owl_name = old_value
            db.commit()
