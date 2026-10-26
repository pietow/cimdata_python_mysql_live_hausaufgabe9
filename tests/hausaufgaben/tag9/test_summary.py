"""Vorgegebene Tests zu Aufgabe 2. Diese Datei nicht verändern."""
import pytest


def summary_url(student_id):
    return f"/students/{student_id}/booking-summary"


def test_without_login(client, sample):
    response = client.get(summary_url(sample["harry_id"]))
    assert response.status_code == 401


def test_reader_is_forbidden(client, headers, sample):
    response = client.get(summary_url(sample["harry_id"]), headers=headers["reader"])
    assert response.status_code == 403


def test_unknown_student(client, headers, sample):
    response = client.get(summary_url(sample["missing_id"]), headers=headers["staff"])
    assert response.status_code == 404


@pytest.mark.parametrize("key,name,count", [
    ("harry_id", "Harry Potter", 3),
    ("hermione_id", "Hermione Granger", 1),
    ("neville_id", "Neville Longbottom", 0),
])
def test_complete_summary(client, headers, sample, key, name, count):
    response = client.get(summary_url(sample[key]), headers=headers["staff"])
    assert response.status_code == 200
    data = response.json()
    assert data == {
        "student_id": sample[key],
        "student_name": name,
        "booking_count": count,
    }
    assert type(data["student_id"]) is int
    assert type(data["booking_count"]) is int


@pytest.mark.parametrize("value", [0, -1, "kein-integer"])
def test_invalid_student_id(client, headers, value):
    response = client.get(summary_url(value), headers=headers["staff"])
    assert response.status_code == 422


def test_response_model_is_documented(client):
    # response_model soll auch in der automatisch erzeugten API-Doku erscheinen.
    spec = client.get("/openapi.json").json()
    schema = spec["paths"][summary_url("{student_id}")]["get"]["responses"]["200"]["content"]["application/json"]["schema"]
    if "$ref" in schema:
        schema = spec["components"]["schemas"][schema["$ref"].rsplit("/", 1)[-1]]
    assert set(schema.get("required", [])) == {"student_id", "student_name", "booking_count"}
    properties = schema["properties"]
    assert set(properties) == {"student_id", "student_name", "booking_count"}
    assert properties["student_id"]["type"] == "integer"
    assert properties["student_name"]["type"] == "string"
    assert properties["booking_count"]["type"] == "integer"
