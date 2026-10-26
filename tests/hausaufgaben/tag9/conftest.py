"""Bereitgestellte Fixtures: echte Hausaufgaben-DB und echte Anmeldung."""
import pytest
from fastapi.testclient import TestClient

@pytest.fixture(scope="session")
def sample():
    from hausaufgabe9.seed import seed
    return seed()

@pytest.fixture(scope="session")
def client(sample):
    from hausaufgabe9.main import app
    with TestClient(app) as client:
        yield client

@pytest.fixture(scope="session")
def headers(client):
    from hausaufgabe9.seed import PASSWORD
    result={}
    try:
        for role,username in (("staff","mcgonagall"),("reader","flitwick")):
            response=client.post("/auth/login",json={"username":username,"password":PASSWORD})
            assert response.status_code==200, "Vorprüfung: Anmeldung aus Tag 9 funktioniert nicht."
            result[role]={"Authorization":"Bearer "+response.json()["access_token"]}
        yield result
    finally:
        for value in result.values():
            client.post("/auth/logout",headers=value)


@pytest.fixture
def db_factory(sample):
    # Eine normale Session-Fabrik, kein Mock und kein eigener Datenbestand.
    from hausaufgabe9.database import SessionLocal
    return SessionLocal
