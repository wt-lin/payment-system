from pydantic import BaseModel
from uuid import UUID

class PaymentEventSchema(BaseModel):
    event_id: str
    payment_id: UUID
    type: str
