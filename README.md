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


