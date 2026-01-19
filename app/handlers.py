from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from fastapi import HTTPException

from .models import Payment, PaymentEvent
from .logic import evaluate_transition, TransitionResult

def process_event(db: Session, event):
    """
    Orchestrates a single payment event inside one DB transaction.
    """
    try:
        with db.begin():
            # 1. Load or create payment
            payment = db.get(Payment, event.payment_id)
            if not payment:
                payment = Payment(
                    id=event.payment_id,
                    state="created",
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                )
                db.add(payment)
                db.flush()

            # 2. Insert event first (idempotency)
            payment_event = PaymentEvent(
                event_id=event.event_id,
                payment_id=payment.id,
                event_type=event.type,
                status="received",
                created_at=datetime.utcnow(),
            )
            db.add(payment_event)
            db.flush()  # PK constraint enforced here

            # 3. Evaluate state transition
            result, new_state = evaluate_transition(payment.state, event.type)

            if result == TransitionResult.APPLY:
                payment.state = new_state
                payment.updated_at = datetime.utcnow()
                payment_event.status = "applied"

            elif result == TransitionResult.IGNORE:
                payment_event.status = "ignored"
                payment_event.reason = "out_of_order"

            elif result == TransitionResult.MANUAL_REVIEW:
                payment.state = "inconsistent"
                payment.updated_at = datetime.utcnow()
                payment_event.status = "manual_review"

            elif result == TransitionResult.REJECT:
                payment_event.status = "rejected"
                payment_event.reason = "invalid_transition"
                raise HTTPException(
                    status_code=400,
                    detail="Invalid state transition"
                )

            return {
                "status": payment_event.status,
                "payment_state": payment.state,
            }

    except IntegrityError:
        db.rollback()
        return {
            "status": "noop",
            "reason": "duplicate_event"
        }