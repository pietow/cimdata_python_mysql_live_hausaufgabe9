# Hogwarts – Hausaufgabe Tag 9

Ihr implementiert eine geschützte Buchungsübersicht, ergänzt ein Modell mit
einer Alembic-Migration und ergänzt eine Funktion anhand vorgegebener Tests. Dieses Repository enthält
das ungelöste Startgerüst und die dafür benötigten Teile des Kursprojekts.

## Einstieg

Beginnt mit dem [Hausaufgabenblatt](docs/hausaufgaben/09-Buchungsübersicht.md).
Es beschreibt das vollständige Setup, die Aufgaben, die Prüfungen und die Abgabe.
Die Abgabe erfolgt über euer eigenes GitHub-Repository bis **Freitag, 30. Oktober
2026, 14:00 Uhr (Berliner Zeit)**. Anschließend findet das Codegespräch statt.
Die Git-Befehle stehen im Abgabeabschnitt des Hausaufgabenblatts.
Die [Postman-Collection](docs/postman/09-Hausaufgabe.postman_collection.json)
unterstützt euch beim manuellen Prüfen der Hausaufgaben-API.

## Eigene Umgebung einrichten

Im Terminal dieses Projektordners eine eigene Umgebung einrichten:

```powershell
python -m venv .venv
& .\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-hausaufgabe.txt
python -m pytest --version
python -c "import httpx2; print(httpx2.__version__)"
python -m pip check
```

- Bei bereits eingerichteter `.venv` genügen Aktivierung und Paketprüfung.
- `requirements-hausaufgabe.txt` dokumentiert alle benötigten Pakete an einer Stelle.
- `.env.hausaufgabe.example` ist die Vorlage für eure lokale Konfiguration.
- Die Hausaufgabe verwendet eine eigene Datenbank `hogwarts_hausaufgabe` auf Port `3309`.
- Die normale Live-Kurskopie und ihre Datenbank bleiben unverändert.

## Dateien und Ordner

```text
hausaufgabe9/                  Aufgaben-Gerüst, Konfiguration und Beispieldaten
tag7/                         Bekannte Datenbankanbindung und Modelle
tag9/                         Bekannte Authentifizierung und Rollenprüfung
tests/hausaufgaben/tag9/       Vollständige Tests und gemeinsame Fixtures
alembic.ini                   Einzige Alembic-Konfiguration
alembic/                      Migrationsumgebung und Revisionen 0001 bis 0003
compose.hausaufgabe.yaml       Eigener MySQL-Container
requirements-hausaufgabe.txt   Abhängigkeiten der Hausaufgabe
docs/                         Hausaufgabenblatt und passende Postman-Collection
```

- `tag7` und `tag9` behalten ihre Namen, damit die bekannten Imports funktionieren.
- `alembic/env.py` lädt immer die Hausaufgabenkonfiguration vor der Datenbank-Engine.
- Alembic verwendet automatisch `alembic.ini`; eine Auswahl mit `-c` ist nicht nötig.
- Vor dem Modellumbau erst auf `0003` migrieren und Beispieldaten anlegen.
- Neue Spalte, API-Implementierung und Migration erarbeitet ihr selbst.
- Aufgabe 4 wird ausschließlich durch die vorgegebenen Tests beschrieben.
- `python -m pytest -q` sucht nur in `tests/hausaufgaben/tag9`.
- Alle Tests sind vorgegeben; verändert weder die Tests noch ihre Fixtures.
- Im ungelösten Gerüst schlagen fachliche Tests erwartungsgemäß fehl.
- Für Tag 10 wieder zur unveränderten Live-Kurskopie wechseln.

## Aufgaben überprüfen

```powershell
python -m pytest tests/hausaufgaben/tag9/test_summary.py -q
python -m pytest tests/hausaufgaben/tag9/test_owl_name.py -q
python -m pytest tests/hausaufgaben/tag9/test_course_list.py -q
```

Die Tests verwenden dieselbe Hausaufgaben-Datenbank und laufen nacheinander.
Für Aufgabe 3 zuerst die eigene Migration anwenden. Zum Abschluss alle Tests
mit `python -m pytest -q` ausführen.

Die Postman-Collection wird mitgeliefert. Nur die lokale Environment-Datei
`hausaufgabe9.postman_environment.json` wird mit `python -m hausaufgabe9.seed`
erzeugt. Die vollständige Request-Übersicht steht im Hausaufgabenblatt.

## Für die Weitergabe

- Den gesamten Projektordner ohne `Dozent/` weitergeben.
- Keine Teilnehmerdatei benötigt Dateien aus `Dozent/`.
- Lokale `.env`-Dateien, `.venv` und die erzeugte Postman-Umgebung nicht weitergeben.
