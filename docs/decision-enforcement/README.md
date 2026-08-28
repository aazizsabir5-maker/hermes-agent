# Decision-Enforcement Documentation

This directory makes the fork self-contained for future contributors and fresh AI sessions.

## Read in this order

1. [`../../NORTH_STAR.md`](../../NORTH_STAR.md) — authoritative purpose, product promise, single enforceable rule, scope, non-goals, and change test.
2. [`PRODUCT-DECISIONS.md`](PRODUCT-DECISIONS.md) — user-confirmed direction, proposed corrections, and explicit reopening conditions.
3. [`CURRENT-STATE.md`](CURRENT-STATE.md) — what exists today, why it became excessive, current launcher behavior, known operational failures, and repository architecture.
4. [`CORRECTION-PLAN.md`](CORRECTION-PLAN.md) — task-by-task TDD plan for simplifying the fork.
5. [`HANDOFF.md`](HANDOFF.md) — copy-paste context for a fresh chat or implementation agent.
6. [`../design-enforcement.md`](../design-enforcement.md) — legacy strict-enforcement architecture. This remains historical input until the correction plan replaces it.

## One-sentence objective

Make `hermes 1` enforce comprehensive hierarchical design decisions without requiring users to operate review receipts, modes, manifests, snapshots, or backend stages.

## Current status

The strict fork is implemented and has successfully released a trusted finalization result, but its workflow and backend footprint exceed the intended product. The lean correction is planned but not yet implemented.

Do not begin deleting strict-enforcement code by intuition. Read the North Star, current-state inventory, and correction plan first. Preserve current upstream Hermes behavior while removing only machinery that does not trace to the single enforceable rule.
