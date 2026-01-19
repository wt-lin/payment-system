from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from .db import SessionLocal
from .schemas import PaymentEventSchema
from .handlers import process_event

app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/events")
def handle_event(
    event: PaymentEventSchema,
    db: Session = Depends(get_db)
):
    return process_event(db, event)
