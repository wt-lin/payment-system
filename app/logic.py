from enum import Enum
from typing import Optional


class TransitionResult(Enum):
    APPLY = "apply"
    IGNORE = "ignore"
    REJECT = "reject"
    MANUAL_REVIEW = "manual_review"


def evaluate_transition(current_state: str, event_type: str) -> tuple[TransitionResult, Optional[str]]:
    LEGAL = {
        ("created", "authorize"): "authorized",
        ("created", "fail"): "failed",
        ("authorized", "capture"): "captured",
        ("authorized", "fail"): "failed",
        ("captured", "refund"): "refunded",
    }

    if (current_state, event_type) in LEGAL:
        return TransitionResult.APPLY, LEGAL[(current_state, event_type)]

    ILLEGAL = {
        ("captured", "authorize"): TransitionResult.IGNORE,
        ("refunded", "capture"): TransitionResult.MANUAL_REVIEW,
        ("failed", "authorize"): TransitionResult.REJECT,
        ("failed", "capture"): TransitionResult.REJECT,
        ("created", "capture"): TransitionResult.REJECT,
        ("created", "refund"): TransitionResult.REJECT,
    }

    return ILLEGAL.get(
        (current_state, event_type),
        TransitionResult.REJECT
    ), None
