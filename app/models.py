from sqlalchemy import Column, String, Text, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
import uuid
from .db import Base


class Payment(Base):
    __tablename__ = "payments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    state = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)


class PaymentEvent(Base):
    __tablename__ = "payment_events"

    event_id = Column(Text, primary_key=True)
    payment_id = Column(UUID(as_uuid=True), ForeignKey("payments.id"))
    event_type = Column(Text, nullable=False)
    status = Column(Text, nullable=False)
    reason = Column(Text)
    created_at = Column(TIMESTAMP)
