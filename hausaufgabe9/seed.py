"""Bereitgestellter, wiederholbarer Seeder. Löscht keine Daten."""
import json
from datetime import date
from sqlalchemy import func, select
from hausaufgabe9.database import SessionLocal, check_database
from hausaufgabe9.config import ROOT
from tag7.models import Student, Course, Booking
from tag9.models import User, AccessToken
from tag9.passwords import hash_password

PASSWORD = "Nur-fuer-Hogwarts-Tests-1993!"

def seed():
    check_database()
    with SessionLocal.begin() as db:
        populated = any(db.scalar(select(func.count()).select_from(model))
                        for model in (Student, Course, Booking, User, AccessToken))
        if not populated:
            db.add_all([User(username="mcgonagall", role="staff", password_hash=hash_password(PASSWORD)),
                        User(username="flitwick", role="reader", password_hash=hash_password(PASSWORD))])
            # Explizite unterschiedliche IDs zeigen: ID ist kein Listenindex.
            db.add_all([
                Student(id=11, first_name="Harry", last_name="Potter", house="Gryffindor", school_year=3),
                Student(id=23, first_name="Hermione", last_name="Granger", house="Gryffindor", school_year=3),
                Student(id=37, first_name="Neville", last_name="Longbottom", house="Gryffindor", school_year=3),
                Course(id=101, title="Verwandlung"), Course(id=102, title="Zauberkunst"),
                Course(id=103, title="Kräuterkunde"),
            ])
            db.flush()
            for student_id, course_id in ((11,101),(11,102),(11,103),(23,101)):
                db.add(Booking(student_id=student_id, course_id=course_id, booking_date=date(1993,9,1)))
        db.flush()
        # Fremde oder veränderte Bestände nicht stillschweigend überschreiben.
        expected = [(11,"Harry","Potter",3),(23,"Hermione","Granger",1),(37,"Neville","Longbottom",0)]
        if db.scalar(select(func.count()).select_from(Student)) != 3:
            raise RuntimeError("Unerwarteter Bestand; Lehrkraft informieren.")
        for sid, first, last, count in expected:
            student=db.get(Student,sid)
            actual=db.scalar(select(func.count(Booking.id)).where(Booking.student_id==sid))
            if student is None or (student.first_name,student.last_name,actual)!=(first,last,count):
                raise RuntimeError("Beispieldaten verändert; Lehrkraft informieren.")
        for username,role in (("mcgonagall","staff"),("flitwick","reader")):
            user=db.scalar(select(User).where(User.username==username))
            if user is None or user.role!=role or not user.is_active:
                raise RuntimeError("Demo-Konto fehlt oder wurde verändert.")
        missing=db.scalar(select(func.max(Student.id)))+1000
    return {"harry_id":11,"hermione_id":23,"neville_id":37,"missing_id":missing}

if __name__ == "__main__":
    values={"base_url":"http://127.0.0.1:8009","password":PASSWORD,
            "staff_token":"","reader_token":"",**seed()}
    environment={"name":"Hogwarts Hausaufgabe lokal","values":[
        {"key":key,"value":str(value),"enabled":True,"type":"secret" if key=="password" or "token" in key else "default"}
        for key,value in values.items()],"_postman_variable_scope":"environment"}
    path=ROOT/"hausaufgabe9.postman_environment.json"
    path.write_text(json.dumps(environment,ensure_ascii=False,indent=2),encoding="utf-8")
    print("Seeder geprüft. Postman-Umgebung:",path.name)
