# Hausaufgabe bis Tag 9: Buchungsübersicht und Migration

Ihr entwickelt eine geschützte Übersicht, erweitert ein Modell und implementiert eine weitere Funktion anhand vorgegebener Tests.

**Alle Tests sind vollständig bereitgestellt. Verändert weder die Tests noch ihre Fixtures. Eure Aufgabe ist es, den Anwendungscode zu vervollständigen und die Testergebnisse zu verstehen.**

- **Abgabe über Git/GitHub: Freitag, 30. Oktober 2026, bis 14:00 Uhr. Anschließend findet das Codegespräch statt.**
- Arbeitet nur in `cimdata_python_mysql_live_hausaufgabe9`.
- Dies ist eine eigenständige Kopie des Projekts bis Revision `0003`.
- Die benötigten Modelle und Authentifizierungsbausteine aus tag7 und tag9 sind enthalten.
- Die normale Live-Kurskopie und ihre Datenbank bleiben unverändert.
- KI ist erlaubt. Ihr müsst den Code erklären und verändern können.

## 1. Setup vollständig durchführen

### Eigene Python-Umgebung einrichten

Docker Desktop starten und diese Projektkopie in VS Code öffnen.
Erstellt im Projektordner eine eigene virtuelle Umgebung und installiert die bereitgestellten Abhängigkeiten:

```powershell
python -m venv .venv
& .\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-hausaufgabe.txt
python -m pytest --version
python -c "import httpx2; print(httpx2.__version__)"
python -m pip check
Copy-Item .env.hausaufgabe.example .env.hausaufgabe
```

- Falls `.venv` bereits eingerichtet ist, genügen Aktivierung und Paketprüfung.
- Die Requirements-Datei enthält alle benötigten Abhängigkeiten.
- Eine bereits ausgefüllte `.env.hausaufgabe` nicht erneut überschreiben.
- Bei belegtem Port `HW_DB_PORT` ändern; Standard ist `3309`.
- In `.env.hausaufgabe` beide Passwortplatzhalter ersetzen.
- Keine normale `.env` aus dem Live-Projekt in diese Kopie übernehmen.
- `.env.hausaufgabe` weder abgeben noch veröffentlichen.

### Eigene Datenbank und Ausgangsstand vorbereiten

```powershell
$hw = @("--env-file", ".env.hausaufgabe", "-f", "compose.hausaufgabe.yaml")
docker compose @hw up -d --wait db
python -m alembic upgrade 0003
python -m hausaufgabe9.seed
python -m alembic current
```

**Erst bei Revision 0003 und vorhandenem Seed das Modell ändern.**

- Alle Hausaufgabenbefehle laufen aus diesem Projektroot.
- Alembic verwendet automatisch die einzige Konfiguration `alembic.ini`.
- `alembic/env.py` lädt die Hausaufgabenkonfiguration vor der Engine.
- Das Datenbankschema entsteht durch die bekannten Migrationen.
- Verwendet ausschließlich `hogwarts_hausaufgabe`.
- Der Seeder legt feste Daten an und prüft sie bei weiteren Aufrufen.
- `python -m hausaufgabe9.seed` erzeugt zusätzlich `hausaufgabe9.postman_environment.json` im Projektroot. Die Postman-Collection ist bereits im Repository enthalten (siehe Abschnitt 5).
- Er löscht keinen Bestand und überschreibt keine veränderten Daten.
- Nach Modelländerung die eigene Migration anwenden, nicht neu initialisieren.

| Daten | Zweck |
| --- | --- |
| mcgonagall, staff | Darf die Übersicht lesen |
| flitwick, reader | Darf die Verwaltungsübersicht nicht lesen |
| Harry Potter | Drei Buchungen: Verwandlung, Zauberkunst, Kräuterkunde |
| Hermione Granger | Eine Buchung: Verwandlung |
| Neville Longbottom | Keine Buchung |

Die Rollen sind eine Übungsentscheidung.
Das lokale API-Testpasswort ist `Nur-fuer-Hogwarts-Tests-1993!` und gilt für mcgonagall und flitwick.

## 2. Buchungsübersicht implementieren

McGonagall möchte die Buchungsanzahl eines einzelnen Schülers sehen.

```http
GET /students/{student_id}/booking-summary
```

Beispiel für Harry aus dem mitgelieferten Seeder:

```json
{"student_id": 11, "student_name": "Harry Potter", "booking_count": 3}
```

| Anfrage | Erwartete Antwort |
| --- | --- |
| `staff`, Schüler mit Buchungen | 200; genau die drei gezeigten Felder. |
| `staff`, Schüler ohne Buchung | 200; `booking_count` ist 0. |
| `staff`, unbekannter Schüler | 404. |
| Ohne Anmeldung | 401. |
| Als `reader` angemeldet | 403. |
| `staff`, ID ist 0, negativ oder Text | 422. |

- Bearbeitet `hausaufgabe9/schemas.py` und `hausaufgabe9/summary.py`.
- Verwendet ein Pydantic-Antwortschema mit `response_model`.
- Verwendet SQLAlchemy und die bekannte Session- und Rollen-Dependency aus Tag 9.
- **Namen, IDs und Anzahlen müssen aus der Datenbank kommen.**
- Zählt nur Buchungen des angefragten Schülers, über alle seine Kurse.
- Der Name besteht aus Vorname, Leerzeichen und Nachname.
- Die Route verändert keine Daten. Anmeldung und Router-Einbindung sind vorbereitet.

### Aufgabe 2 überprüfen

Nach dem Setup und nach jeder Änderung an der Buchungsübersicht:

```powershell
python -m pytest tests/hausaufgaben/tag9/test_summary.py -q
```

Für den ersten Fehler mit ausführlicher Rückmeldung:

```powershell
python -m pytest tests/hausaufgaben/tag9/test_summary.py -x -vv
```

Diese Tests prüfen Anmeldung, Rolle, Antworten, IDs und das Antwortschema. Sie funktionieren bereits auf Revision `0003`. Sobald ihr das Modell in Aufgabe 3 ändert, müsst ihr vor weiteren API-Tests auch die Migration anwenden.

## 3. Das Modell minimal erweitern

Hogwarts möchte bei Schülern optional den Namen ihrer Posteule speichern.

1. Ergänzt `owl_name` in der Klasse `Student` in `tag7/models.py`.
2. Das Feld ist eine Zeichenkette mit höchstens 50 Zeichen auf Datenbankebene.
3. Ein fehlender Name ist erlaubt: Python `None`, SQL `NULL`.
4. Nutzt den vorhandenen Stil mit `Mapped` und `mapped_column`.
5. Erzeugt die Migration **aus dem geänderten Modell**:

```powershell
python -m alembic revision `
  --autogenerate --rev-id hw9_owl -m "student owl name"
```

6. Öffnet die neue Datei in `alembic/versions` und prüft sie vor dem Ausführen.
7. `upgrade()` soll nur diese Spalte ergänzen. `downgrade()` soll nur diese Spalte entfernen.
8. `down_revision` muss auf `0003` verweisen. Bei weiteren Änderungen: stoppen und Ursache klären.
9. Ergänzt in der Migrationsdatei drei kurze Kommentare in eigenen Worten:
   - Was vergleicht `--autogenerate`?
   - Warum ändert das Bearbeiten von `models.py` allein die Tabelle nicht?
   - Warum führt `stamp` diese Schemaänderung nicht aus?

```powershell
python -m alembic upgrade hw9_owl
python -m alembic current
python -m alembic history
python -m alembic check
```

| Befehl | Prüft oder bewirkt |
| --- | --- |
| `revision --autogenerate` | Erzeugt einen Entwurf aus Modellmetadaten und vorhandenem DB-Schema. |
| `upgrade hw9_owl` | Führt die Migration auf der Datenbank aus. |
| `current` | Zeigt den gespeicherten Revisionsstand. |
| `history` | Zeigt die Reihenfolge der vorhandenen Migrationen. |
| `check` | Prüft, ob Autogenerate noch Schemaunterschiede erkennen würde. Es prüft keine API-Logik. |

**Bestehende Schüler und Buchungen bleiben erhalten. Die neue Spalte enthält zunächst `NULL`.**

Prüft das direkt in MySQL, bevor ihr mit den Tests Werte speichert:

```powershell
docker compose @hw exec db mysql -u homework -p hogwarts_hausaufgabe
```

Gebt `HW_DB_PASSWORD` aus `.env.hausaufgabe` ein. In der MySQL-Konsole:

```sql
SHOW COLUMNS FROM students LIKE 'owl_name';
SELECT id, first_name, last_name, owl_name FROM students ORDER BY id;
SELECT COUNT(*) AS booking_count FROM bookings;
exit;
```

- Erwartet: `varchar(50)`, `Null: YES`, drei vorhandene Schüler mit `NULL` und vier Buchungen.
- Für `owl_name` braucht ihr keinen neuen Endpunkt. Die Buchungsübersicht bleibt bei drei Antwortfeldern.
- Verwendet weder `create_all()` noch `stamp` als Ersatz für `upgrade`.
- Kein Downgrade im normalen Testlauf: Es würde gespeicherte Eulennamen löschen.

### Aufgabe 3 überprüfen

Erst nach `upgrade hw9_owl` und der direkten MySQL-Prüfung:

```powershell
python -m pytest tests/hausaufgaben/tag9/test_owl_name.py -q
```

Die Tests prüfen das Modell, die echte MySQL-Spalte, die Revisionskette, das Speichern in einer neuen Session und das Zurücksetzen auf `None`. Gespeicherte Eulennamen werden am Testende wiederhergestellt. Die drei Kommentare und den ausschließlich auf `owl_name` begrenzten Inhalt der Migration prüft ihr zusätzlich selbst; das wird auch im Codegespräch besprochen.

## 4. Neue Funktion ausschließlich aus Tests ableiten

Öffnet **`tests/hausaufgaben/tag9/test_course_list.py`**. Diese Tests sind eure fachliche Aufgabenbeschreibung. Eine zusätzliche Beschreibung des Endpunkts und seiner Antworten gibt es hier bewusst nicht.

1. Lest zuerst die Tests, ohne Anwendungscode zu ändern. Achtet auf Vorbereitung, Request und Assertions.
2. Leitet daraus ab: Welche Route fehlt? Wer darf sie verwenden? Wie müssen Antworten und Fehlerfälle aussehen? Welche Reihenfolge wird erwartet? Welche Daten müssen aus MySQL kommen?
3. Notiert eure Schlussfolgerungen als kurze Kommentare oben in `hausaufgabe9/course_list.py`. Verweist bei mindestens zwei Schlussfolgerungen auf den betreffenden Testnamen.
4. Führt die Tests aus und lest die erste Fehlermeldung.
5. Implementiert die fehlende Funktion in `hausaufgabe9/course_list.py`. Der leere Router ist bereits in `main.py` eingebunden. Falls nötig, ergänzt Antwortschemas in `hausaufgabe9/schemas.py`.
6. Wiederholt den Testlauf, bis alle Tests bestehen. Verwendet die echten Datenbankdaten; schreibt erwartete Namen, IDs oder Ergebnislisten nicht fest in den Anwendungscode.


```powershell
python -m pytest tests/hausaufgaben/tag9/test_course_list.py -x -vv
```

Danach ohne Abbruch beim ersten Fehler:

```powershell
python -m pytest tests/hausaufgaben/tag9/test_course_list.py -q
```

Eine zusätzliche Migration ist für Aufgabe 4 nicht erforderlich. Die Tests und `conftest.py` bleiben unverändert. Bearbeitet den Anwendungscode, bis er den Anforderungen entspricht.

## 5. Tests und Postman im Überblick

### Automatische Prüfungen

| Aufgabe | Vorgegebene Testdatei | Was ihr bearbeitet |
| --- | --- | --- |
| 2 | `tests/hausaufgaben/tag9/test_summary.py` | `hausaufgabe9/summary.py`, `hausaufgabe9/schemas.py` |
| 3 | `tests/hausaufgaben/tag9/test_owl_name.py` | `tag7/models.py` und eure neue Migration |
| 4 | `tests/hausaufgaben/tag9/test_course_list.py` | `hausaufgabe9/course_list.py`, bei Bedarf Antwortschemas |

Abschließend alle Tests ausführen:

```powershell
python -m pytest tests/hausaufgaben/tag9 -q

```

- MySQL muss laufen. Nach Aufgabe 3 muss Revision `hw9_owl` angewendet sein.
- Ein laufender Uvicorn-Server ist für pytest nicht nötig; `TestClient` ruft die App direkt auf.
- Die Tests laufen auf `hogwarts_hausaufgabe`, nicht auf der Kursdatenbank. Es gibt keine zusätzliche Testdatenbank.
- Anmeldung und Datenbankzugriffe sind echt. Die bereitgestellten Tests stellen ihre Datenänderungen wieder her und melden ihre Tokens ab.
- Nicht parallel ausführen: Die Tests verwenden denselben Beispieldatenbestand.
- Fehlgeschlagene Tests sind im Startgerüst erwartet. `ERROR` beim Setup, fehlende Pakete oder eine nicht erreichbare DB müsst ihr zuerst beheben.
- Ein `FAILED` zeigt die nicht erfüllte Prüfung. Lest dazu Testname, Request und erwarteten gegenüber dem tatsächlichen Wert.
- Weder Tests löschen/abschalten noch Assertions abschwächen.

Zum Lesen der Tests helfen diese bereitgestellten Fixtures:

| Fixture | Bedeutung |
| --- | --- |
| `client` | FastAPI-TestClient |
| `headers` | Echte Anmeldung für `headers["staff"]` und `headers["reader"]` |
| `sample` | Schüler-IDs und eine sicher fehlende ID |
| `db_factory` | Session-Fabrik für echte MySQL-Sessions |

### Welche Postman-Datei kommt woher?

| Datei | Herkunft und Zweck |
| --- | --- |
| `docs/postman/09-Hausaufgabe.postman_collection.json` | Wird mitgeliefert. Enthält Requests und Antwortprüfungen für Aufgabe 2.  |
| `hausaufgabe9.postman_environment.json` | Wird ausschließlich durch `python -m hausaufgabe9.seed` erzeugt. Enthält Basis-URL, Schüler-IDs, lokales API-Testpasswort und zunächst leere Tokenfelder. Nicht abgeben oder veröffentlichen. |

Der Aufruf der Fixture `sample` prüft die Beispieldaten, schreibt aber keine Postman-Datei. Ein erneuter CLI-Aufruf des Seeders erzeugt die Environment-Datei erneut mit leeren Tokens. Danach in Postman neu importieren und erneut anmelden. Die Tokens werden erst durch die Login-Requests in der ausgewählten Postman-Umgebung gespeichert.

### Postman verwenden

```powershell
python -m hausaufgabe9.seed
python -m uvicorn hausaufgabe9.main:app --host 127.0.0.1 --port 8009
```

1. Die mitgelieferte Collection importieren.
2. Die erzeugte Environment-Datei importieren und als aktive Umgebung auswählen.
3. Die Collection von oben nach unten ausführen: zwei Logins → API-Fälle → zwei Logouts.
4. Statuscode, JSON-Antwort und „Test Results“ prüfen.

| Schritt | Request / Rolle | Erwartung nach Aufgabe 2 |
| --- | --- | --- |
| Login | `POST /auth/login`, mcgonagall und flitwick | Je 200; speichert staff- bzw. reader-Token |
| Ohne Anmeldung | `GET /students/{{harry_id}}/booking-summary` | 401 |
| Reader | Dieselbe Route mit reader-Token | 403 |
| Unbekannter Schüler | ID `{{missing_id}}`, staff | 404 |
| Harry | ID `{{harry_id}}`, staff | 200; vollständige Antwort, Anzahl 3 |
| Hermione | ID `{{hermione_id}}`, staff | 200; vollständige Antwort, Anzahl 1 |
| Neville | ID `{{neville_id}}`, staff | 200; vollständige Antwort, Anzahl 0 |
| Ungültige IDs | `0`, `-1`, `kein-integer`, staff | Je 422 |
| Logout | `POST /auth/logout`, je einmal pro Rolle | Je 204 |

- Insgesamt enthält die Collection 13 Requests. Alle Antworten beziehen sich auf die mitgelieferten Beispieldaten.
- `owl_name` prüft ihr mit MySQL und `test_owl_name.py`; dafür wird kein Endpunkt ergänzt.
- Aufgabe 4 ist absichtlich nicht in der Collection beschrieben. Leitet die Anforderungen zuerst aus den Tests ab; anschließend könnt ihr passende Requests selbst in Postman anlegen.
- Postman unterstützt die manuelle Prüfung. Für den Abschluss müssen alle vorgegebenen pytest-Tests bestehen.
- Bei 401 zuerst Login und aktive Umgebung prüfen; bei 403 die Rolle prüfen.
- Uvicorn vor weiteren pytest-Läufen mit `Strg+C` beenden.

## 6. Abgabe und Abschluss

**Abgabe: Freitag, 30. Oktober 2026, bis 14:00 Uhr über euer eigenes GitHub-Repository. Anschließend findet das Codegespräch statt.**

Gebt das vollständige Projekt über Git/GitHub ab. Diese Dateien enthalten eure Lösung und müssen im Repository vorhanden sein:

- `hausaufgabe9/schemas.py`
- `hausaufgabe9/summary.py`
- `hausaufgabe9/course_list.py` einschließlich eurer aus Tests abgeleiteten Kommentare
- `tag7/models.py`
- Eure neue Migrationsdatei aus `alembic/versions`.

- Das Startgerüst und die vorgegebenen Tests bleiben im Repository enthalten. Die Tests und Fixtures bleiben unverändert und werden nicht als eigene Leistung bewertet.
- Keine `.env`-Dateien mit Zugangsdaten, `.venv`, Datenbankdateien, erzeugte Postman-Umgebung oder `Dozent/` hochladen. Die Vorlage `.env.hausaufgabe.example` gehört zum Projekt.
- Falls ihr KI verwendet habt: höchstens drei kurze Kommentarzeilen am Ende von `summary.py` zu Nutzung und eigener Prüfung.
- Bewertung: Umsetzung und kurzes Codegespräch

### GitHub-Repository einmalig vorbereiten

Erstellt auf GitHub ein eigenes leeres Repository, zum Beispiel `hausaufgabe9-vorname-nachname`. Legt dort zunächst keine README, `.gitignore` oder Lizenz an; die Projektdateien bringt ihr aus diesem Ordner mit. Stellt sicher, dass die Lehrkraft Zugriff auf das Repository hat.

Alle folgenden Git-Befehle laufen im Projektordner. Falls der Ordner noch kein Git-Repository ist, initialisiert ihn einmal:

```powershell
git init
```

Prüft danach, welches GitHub-Repository als Ziel eingetragen ist:

```powershell
git remote -v
```

Wenn noch kein `origin` vorhanden ist, fügt euer eigenes Repository hinzu. Ersetzt die Beispiel-URL durch die URL eures Repositorys:

```powershell
git remote add origin "https://github.com/DEIN-NAME/DEIN-REPOSITORY.git"
```

Falls `origin` bereits auf das Unterrichtsrepository oder ein anderes Repository zeigt, ändert stattdessen die Adresse:

```powershell
git remote set-url origin "https://github.com/DEIN-NAME/DEIN-REPOSITORY.git"
git remote -v
```

### Lösung prüfen, committen und hochladen

```powershell
python -m pytest tests/hausaufgaben/tag9 -q
git status --short
git add .
```

Anschließend speichern und zu eurem GitHub-Repository übertragen:

```powershell
git commit -m "Hausaufgabe Tag 9: API, Migration und testbasierte Funktion"
git push 
```

Für spätere Korrekturen wiederholt ihr Testlauf, `git add .` und `git commit` mit einer passenden Nachricht. Danach genügt `git push`.

### Was zählt als Abgabe?

- Öffnet euer Repository auf GitHub und prüft, ob der letzte Commit, alle Lösungsdateien und die neue Migration im abgegebenen Branch sichtbar sind.
- Teilt der Lehrkraft bis Freitag, 30. Oktober 2026, 14:00 Uhr den Repository-Link, den Branch-Namen und die kurze Commit-ID aus `git log -1 --oneline` mit.
- Maßgeblich ist der bis zur Frist auf GitHub hochgeladene und benannte Commit. Ein lokaler Commit ohne erfolgreichen Push ist keine vollständige Abgabe.
- Eine ZIP-Abgabe ist nicht erforderlich.

### Anschließendes Codegespräch

Das Codegespräch findet am Freitag im Anschluss an die Abgabe um 14:00 Uhr statt. Haltet euren abgegebenen Stand in VS Code bereit; MySQL muss laufen und die Tests müssen ausführbar sein.

Ihr erklärt eine Stelle im Anwendungscode und eine Anforderung aus den Tests. Außerdem führt ihr eine kleine Änderung ohne KI durch. Syntaxhilfe ist erlaubt.

### Datenbank nach dem Codegespräch beenden

```powershell
# In einem neuen Terminal zuerst $hw aus dem Setup erneut setzen.
docker compose @hw down
```

Das Volume bleibt erhalten. `down --volumes` würde die Hausaufgabendaten löschen.
