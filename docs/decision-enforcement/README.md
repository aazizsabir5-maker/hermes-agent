# Decision-Enforcement Documentation

This directory keeps the maintained fork self-contained for contributors and fresh AI sessions.

## Read in this order

1. [`../../NORTH_STAR.md`](../../NORTH_STAR.md) — authoritative purpose, product promise, invariant, scope, and non-claims.
2. [`../../DESIGN-DECISIONS.md`](../../DESIGN-DECISIONS.md) — live boundary, consequential implementation decisions, evidence, and completion status.
3. [`PRODUCT-DECISIONS.md`](PRODUCT-DECISIONS.md) — implemented product decisions and reopening conditions.
4. [`CURRENT-STATE.md`](CURRENT-STATE.md) — implemented architecture, removals, footprint, verification state, and remaining release gates.
5. [`CORRECTION-PLAN.md`](CORRECTION-PLAN.md) — the task-by-task TDD implementation plan and acceptance contract.
6. [`HANDOFF.md`](HANDOFF.md) — copy-paste context and commands for a fresh session.
7. [`../design-enforcement.md`](../design-enforcement.md) — concise user workflow and developer contract.

## Objective

Make `hermes 1` enforce comprehensive hierarchical design decisions without requiring users to operate modes, manifests, receipts, snapshots, reviewer sessions, reconciliation, or backend stages.

## Status

The lean implementation exists on `refactor/lean-decision-enforcement` and is ready for final supervising-agent verification. Do not call it published or production-complete until the uninterrupted tests, fresh independent reviews, installed-copy checks, and Task 10 publication steps recorded in `CURRENT-STATE.md` have passed.
