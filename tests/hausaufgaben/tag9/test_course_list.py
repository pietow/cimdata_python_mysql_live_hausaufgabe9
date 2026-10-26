"""Aufgabe 4: Lies die Tests und leite daraus die Anforderungen ab.

Diese Datei und die Fixtures bleiben unverändert.
"""
import pytest
from sqlalchemy import select
from tag7.models import Booking, Course, Student


def course_url(student_id):
    return f"/students/{student_id}/courses"


def test_without_login(client, sample):
    response = client.get(course_url(sample["harry_id"]))
    assert response.status_code == 401


def test_reader_is_forbidden(client, headers, sample):
    response = client.get(course_url(sample["harry_id"]), headers=headers["reader"])
    assert response.status_code == 403


def test_unknown_student(client, headers, sample):
    response = client.get(course_url(sample["missing_id"]), headers=headers["staff"])
    assert response.status_code == 404


@pytest.mark.parametrize("key,expected_courses", [
    ("harry_id", [
        {"course_id": 103, "title": "Kräuterkunde"},
        {"course_id": 101, "title": "Verwandlung"},
        {"course_id": 102, "title": "Zauberkunst"},
    ]),
    ("hermione_id", [{"course_id": 101, "title": "Verwandlung"}]),
    ("neville_id", []),
])
def test_courses_for_each_student(client, headers, sample, key, expected_courses):
    response = client.get(course_url(sample[key]), headers=headers["staff"])
    assert response.status_code == 200
    data = response.json()
    assert data == {"student_id": sample[key], "courses": expected_courses}
    assert type(data["student_id"]) is int
    for course in data["courses"]:
        assert type(course["course_id"]) is int
        assert type(course["title"]) is str


@pytest.mark.parametrize("value", [0, -1, "kein-integer"])
def test_invalid_student_id(client, headers, value):
    response = client.get(course_url(value), headers=headers["staff"])
    assert response.status_code == 422


def test_request_does_not_change_students_courses_or_bookings(client, headers, sample, db_factory):
    def snapshot():
        with db_factory() as db:
            return (
                list(db.execute(select(Student.__table__).order_by(Student.id))),
                list(db.execute(select(Course.__table__).order_by(Course.id))),
                list(db.execute(select(Booking.__table__).order_by(Booking.id))),
            )

    before = snapshot()
    response = client.get(course_url(sample["harry_id"]), headers=headers["staff"])
    assert response.status_code == 200
    assert snapshot() == before


def test_changed_database_title_is_returned_in_sorted_position(client, headers, sample, db_factory):
    with db_factory() as db:
        old_title = db.get(Course, 101).title
    try:
        with db_factory() as db:
            db.get(Course, 101).title = "Abwehrzauber (Test)"
            db.commit()
        response = client.get(course_url(sample["harry_id"]), headers=headers["staff"])
        assert response.status_code == 200
        assert response.json() == {
            "student_id": sample["harry_id"],
            "courses": [
                {"course_id": 101, "title": "Abwehrzauber (Test)"},
                {"course_id": 103, "title": "Kräuterkunde"},
                {"course_id": 102, "title": "Zauberkunst"},
            ],
        }
    finally:
        with db_factory() as db:
            db.get(Course, 101).title = old_title
            db.commit()
