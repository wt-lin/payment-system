import pytest
from app.logic import evaluate_transition, TransitionResult


def test_authorize_from_created():
    result, new_state = evaluate_transition("created", "authorize")
    assert result == TransitionResult.APPLY
    assert new_state == "authorized"


def test_ignore_out_of_order_authorize():
    result, new_state = evaluate_transition("captured", "authorize")
    assert result == TransitionResult.IGNORE
    assert new_state is None


def test_reject_capture_from_failed():
    result, _ = evaluate_transition("failed", "capture")
    assert result == TransitionResult.REJECT


def test_manual_review_refunded_to_capture():
    result, _ = evaluate_transition("refunded", "capture")
    assert result == TransitionResult.MANUAL_REVIEW
