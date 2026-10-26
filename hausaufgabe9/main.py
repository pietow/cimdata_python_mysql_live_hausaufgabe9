from hausaufgabe9.database import check_database
from fastapi import FastAPI
from tag9.routers import auth
from hausaufgabe9 import course_list, summary

# Kleine Prüf-App: die unveränderte echte Authentifizierung aus Tag 9.
check_database()
app = FastAPI(title="Hogwarts – Hausaufgabe Tag 9")
app.include_router(auth.router)
app.include_router(summary.router)
app.include_router(course_list.router)
