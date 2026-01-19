# Idempotent Payment Event Processor (Deliberately Scoped)

This project is a deliberately scoped backend system that processes **payment events under uncertainty**.

It is not a full payment system.
It is an exploration of **decision boundaries**, **state transitions**, and **risk containment** in payment workflows.

---

## Problem Statement

Payment systems operate in an environment where:

* Events can arrive **out of order**
* Events can be **duplicated**
* External systems may retry aggressively
* Some transitions are **ambiguous or unsafe to automate**

The core problem this project addresses is:

> **How do we process payment events deterministically, without over-automating decisions that should remain reversible or manually reviewed?**

---

## What This Project Intentionally Solves

### 1. Deterministic State Transitions

A payment progresses through a clearly defined state machine:

```
created → authorized → captured → refunded
```

All transitions are explicitly classified as one of:

* `APPLY` — safe, deterministic transition
* `IGNORE` — valid but redundant (e.g. duplicates, out-of-order)
* `REJECT` — invalid and unsafe
* `MANUAL_REVIEW` — ambiguous or high-risk transitions

There is no implicit “success / failure” binary.

---

### 2. Illegal Transition Classification

Instead of throwing errors for all invalid events, the system differentiates:

* **Benign anomalies** (ignored)
* **Hard violations** (rejected)
* **Risky edge cases** (manual review)

Example:

| Current State | Event     | Outcome       |
| ------------- | --------- | ------------- |
| refunded      | capture   | MANUAL_REVIEW |
| captured      | authorize | IGNORE        |
| failed        | capture   | REJECT        |

This reflects real-world payment behavior rather than idealized flows.

---

### 3. Idempotency at the Database Level

Every incoming event carries a unique `event_id`.

* Duplicate events are **no-ops**
* Idempotency is enforced via **database constraints**
* No reliance on in-memory caches or distributed locks

This ensures correctness under retries and partial failures.

---

### 4. Transactional Integrity

Each event is processed inside a single database transaction:

* State transition
* Event persistence
* Idempotency check

Either all effects are committed, or none are.

---

## What This Project Intentionally Does NOT Do

This is important.

The following are deliberately **out of scope**:

* UI or dashboards
* Webhooks or external integrations
* Async processing / message queues
* Retry orchestration
* Metrics and observability pipelines
* Full reconciliation workflows

These are valuable problems, but **they belong to a different risk surface**.

This project stops at the point where:

> further automation would increase blast radius without increasing confidence.

---

## Architecture Overview

```
app/
├── logic.py        # Pure state machine logic (no I/O)
├── handlers.py     # Transactional orchestration
├── models.py       # SQLAlchemy models
├── db.py           # Database setup
├── schemas.py      # Request schemas
└── main.py         # FastAPI entry point
```

### Design Principles

* **Pure logic is isolated and testable**
* **Database is the source of truth**
* **Handlers coordinate, not decide**
* **Risk is classified, not hidden**

---

## Setup & Run

This project is designed to be runnable locally with minimal setup.

### Requirements

* Python 3.10+
* PostgreSQL (local or hosted)
* `pip` or `pipenv`

---

### 1. Create Virtual Environment

```bash
python -m venv .venv
source .venv/bin/activate
```

---

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 3. Configure Environment Variables

Create a `.env` file in the project root:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/payment_demo
```

The database is assumed to already exist.
Schema creation is handled by SQLAlchemy models.

---

### 4. Initialize Database Tables

```bash
python -c "from app.db import Base, engine; Base.metadata.create_all(bind=engine)"
```

---

### 5. Run the Application

```bash
fastapi run --reload
```

The API will be available at:

```
http://localhost:8000
```

---

## Example Request Flow

### 1. Authorize a Payment

```bash
curl -X POST http://localhost:8000/events \
  -H "Content-Type: application/json" \
  -d '{
    "event_id": "evt_1",
    "payment_id": "11111111-1111-1111-1111-111111111111",
    "type": "authorize"
  }'
```

Response (simplified):

```json
{
  "outcome": "APPLY",
  "payment_state": "authorized"
}
```

---

### 2. Capture the Payment

```bash
curl -X POST http://localhost:8000/events \
  -d '{
    "event_id": "evt_2",
    "payment_id": "11111111-1111-1111-1111-111111111111",
    "type": "capture"
  }'
```

---

### 3. Duplicate Event (Idempotent No-op)

```bash
curl -X POST http://localhost:8000/events \
  -d '{
    "event_id": "evt_2",
    "payment_id": "11111111-1111-1111-1111-111111111111",
    "type": "capture"
  }'
```

Response:

```json
{
  "outcome": "IGNORE"
}
```

---

## Testing

```bash
pytest
```

Tests focus on:

* State transition correctness
* Idempotency guarantees
* Transactional integrity

Coverage is secondary to **decision correctness**.

---

## Why This Project Stops Here

In real payment systems, the most dangerous failures are not crashes —
they are **confidently wrong automated decisions**.

This project intentionally stops at the boundary where:

* Automated decisions are safe
* Ambiguous situations are surfaced
* Humans can intervene

That boundary is the point of the exercise.
