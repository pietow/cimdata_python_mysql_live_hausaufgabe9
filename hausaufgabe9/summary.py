from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/students", tags=["Buchungsübersicht"])

@router.get("/{student_id}/booking-summary")
def booking_summary(student_id: int):
    # Aufgabe: Dependency, Rollenprüfung, Schema, Abfrage und Fehlerfälle.
    raise HTTPException(501, "Noch nicht implementiert.")
