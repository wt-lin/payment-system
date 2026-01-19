from uuid import uuid4
from sqlalchemy.orm import Session

from app.handlers import process_event
from app.db import SessionLocal
from app.models import Payment, PaymentEvent


def clear_db(db: Session):
    db.query(PaymentEvent).delete()
    db.query(Payment).delete()
    db.commit()

def test_authorize_then_capture():
    db = SessionLocal()
    clear_db(db)

    payment_id = uuid4()

    r1 = process_event(db, type("E", (), {
        "event_id": "evt_1",
        "payment_id": payment_id,
        "type": "authorize"
    }))

    assert r1["status"] == "applied"
    assert r1["payment_state"] == "authorized"

    r2 = process_event(db, type("E", (), {
        "event_id": "evt_2",
        "payment_id": payment_id,
        "type": "capture"
    }))

    assert r2["status"] == "applied"
    assert r2["payment_state"] == "captured"

def test_duplicate_event_is_noop():
    db = SessionLocal()
    clear_db(db)

    payment_id = uuid4()

    event = {
        "event_id": "evt_dup",
        "payment_id": payment_id,
        "type": "authorize"
    }

    r1 = process_event(db, type("E", (), event))
    r2 = process_event(db, type("E", (), event))

    assert r2["status"] == "noop"

def test_refunded_then_capture_goes_to_manual_review():
    db = SessionLocal()
    clear_db(db)

    payment_id = uuid4()

    process_event(db, type("E", (), {
        "event_id": "e1",
        "payment_id": payment_id,
        "type": "authorize"
    }))

    process_event(db, type("E", (), {
        "event_id": "e2",
        "payment_id": payment_id,
        "type": "capture"
    }))

    process_event(db, type("E", (), {
        "event_id": "e3",
        "payment_id": payment_id,
        "type": "refund"
    }))

    r = process_event(db, type("E", (), {
        "event_id": "e4",
        "payment_id": payment_id,
        "type": "capture"
    }))

    assert r["status"] == "manual_review"
    assert r["payment_state"] == "inconsistent"
