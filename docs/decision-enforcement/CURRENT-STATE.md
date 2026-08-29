# Current State and Architectural Context

## Purpose

This is the current repository handoff for the lean decision-enforcement fork. It records implemented behavior, verification state, remaining release work, and the historical strict system that was removed.

## Repository identity

- Fork: `https://github.com/aazizsabir5-maker/hermes-agent`
- Checkout: `/Users/ariansabir/Developer/hermes-agent-enforced`
- Upstream: `https://github.com/NousResearch/hermes-agent.git`
- Working branch: `refactor/lean-decision-enforcement`
- Current upstream base merged into the branch: `upstream/main` at implementation time
- Publication target: fork `main`, after final verification and independent review

Always inspect live git state; commit identifiers in handoff prose are orientation, not permanent truth.

## Implemented product

The branch implements the reduced guarantee:

> For substantial design work launched with `hermes 1`, Hermes loads the comprehensive decision philosophy, records consequential decisions in an observable ledger, and blocks its own completion claim when that ledger lacks required decision evidence.

The local CLI path now has:

1. A tracked `scripts/hermes-one` launcher targeting the maintained fork and `decision` profile.
2. A hidden launch-context flag; no per-project `.hermes/enforcement.json` or public behavior environment variable.
3. Launch-scoped, cache-stable injection of the full `comprehensive-designer-cognition` skill.
4. Automatic non-overwriting creation of one `DESIGN-DECISIONS.md` ledger for substantial design work.
5. A small deterministic Markdown validator with actionable diagnostics.
6. A mode-free completion gate: ordinary, exploratory, provisional, and next-iteration responses pass; candidate completion claims validate the ledger.
7. One-way migration from the legacy map/records protocol without deleting source files or overwriting an existing ledger.
8. User documentation centered on four actions: enter project, run `hermes 1`, work normally, ask to finish.

## Removed default machinery

The branch removes design-specific requirements for:

- manual working/finalizing modes;
- `.hermes/enforcement.json` project policy state;
- `design_review_request` as a mandatory plugin tool;
- reviewer snapshots, reviewer-only filesystem toolsets, and process/session recursion exceptions;
- HMAC receipts and parent-session/report/subject binding;
- ten universal completion artifacts;
- exact candidate/released-response hashing and durable design audit logs;
- design-policy restrictions across gateway, cron, proxy, media, background, and unrelated delivery paths;
- protected policy shadow/unload/bypass behavior that existed only for strict provenance.

Generic finalization support remains only where the local completion gate uses it.

## Observable contract

`DESIGN-DECISIONS.md` contains:

- boundary and target fidelity;
- parent-to-child decision map with statuses;
- consequential records with criteria, alternatives, selection, tradeoff, evidence, assumptions, consequences, validation, and reopening condition;
- disclosed unresolved consequential decisions;
- fidelity-qualified supported claim and limitations.

The validator checks structural presence, a situation/boundary-to-intent hierarchy, ordered parent links, traceability of every consequential record to an implementation/realization endpoint, status/record relationships, meaningful alternatives, unresolved-ID disclosure, UTF-8/shape limits, and one exact fidelity/scope-qualified supported claim. It does not judge private cognition, semantic quality, or factual truth.

## Current footprint

Relative to current `upstream/main` at the implementation checkpoint:

- 17 production/config/script files changed;
- 1,739 production additions and 11 deletions (net +1,728), excluding tests, docs, and Markdown skill prose;
- one user command: `hermes 1`;
- zero user-managed stages;
- one mandatory project artifact: `DESIGN-DECISIONS.md`;
- zero receipt/snapshot runtime directories required by the design policy.

This is materially smaller than the historical strict fork's 65 changed files and roughly +6,949/-275 lines against its old base.

## Verification state

Completed on the final reviewed implementation:

- strict RED→GREEN cycles for launcher/policy, skill contract, validator, migration, and review-found gaps;
- final focused contract suite: 14 files, 148 tests passed, 0 failed;
- relevant core finalization, prompt, plugin, and launcher regressions repaired and rerun;
- canonical ledger validator: `DESIGN DECISIONS: CONTRACT PASSED`;
- acceptance harness: one ledger, provisional allowance, unsupported-completion blocking, qualified-completion allowance, restart stability, and plain-mode inactivity all passed;
- Ruff on changed Python files, compile checks on changed Python directories, and `git diff --check` passed;
- final independent philosophy/specification and maintainability/code/security reviews passed with no blockers;
- installed decision skill synchronized exactly to the bundled skill and obsolete comprehensive-protocol files removed;
- real installed checks passed for `hermes 1 --version`, `hermes 1 tools list`, plain `hermes --version`, invocation-directory preservation, ledger creation, and unsupported-completion blocking.

Canonical-suite boundary:

- A canonical `scripts/run_tests.sh` run on the reviewed implementation candidate completed with exit 1: 84 test failures across 29 files, three all-pass files with non-zero pytest exits, and four files with no completed tests. None of the 29 failed files was changed relative to `upstream/main`.
- A detached `upstream/main` worktree rerun of all 29 failed files reproduced 84 failures across 28 files. The one-file distribution difference came from timing-sensitive command-token/heartbeat behavior; the failure total and unaffected subsystems were otherwise reproduced without the lean-enforcement diff.
- A second baseline batch covered the seven warning/collection/timeout anomalies: six passed when run outside the full parallel load, while `tests/tools/test_execution_flag_detection.py` completed with three failures on unmodified `upstream/main`.
- A later complete-tree attempt was stopped after 2,342 seconds at 21.9% because of severe timing inflation: 8,298 tests had passed, seven had failed, many files took 200–600 seconds, and `tests/cron/test_scheduler.py` exceeded its 300-second file timeout.
- The full repository suite is therefore not claimed as a pass. The focused changed-surface and acceptance checks remained green, and the upstream-baseline comparison found no failure attributable to the lean decision-enforcement diff.

Publication state:

- fork `main` was fast-forwarded and pushed;
- annotated tag `decision-enforcement-v1` was pushed;
- obsolete `feat/fail-closed-design-enforcement` and `fix/design-enforcement-quickstart` remote branches were deleted only after each reported zero commits unique from published `main`.

## Key files

- `NORTH_STAR.md`
- `DESIGN-DECISIONS.md`
- `docs/design-enforcement.md`
- `docs/decision-enforcement/PRODUCT-DECISIONS.md`
- `docs/decision-enforcement/CORRECTION-PLAN.md`
- `docs/decision-enforcement/HANDOFF.md`
- `scripts/hermes-one`
- `plugins/policies/design_enforcement/`
- `skills/design/comprehensive-designer-cognition/SKILL.md`
- `skills/design/comprehensive-designer-cognition/scripts/validate_design_completion.py`
- `skills/design/comprehensive-designer-cognition/scripts/migrate_to_decision_ledger.py`
- focused tests under `tests/plugins`, `tests/skills`, `tests/hermes_cli`, and relevant `tests/agent` paths.

## Historical context

The previous strict implementation did successfully enforce a trusted finalization on its covered local path, but operation required modes, manifests, snapshots, receipts, session identity, reconciliation, and cross-surface buffering. The correction intentionally gives up those provenance/security claims. Do not restore them by inertia or maintain strict and lean modes in parallel.
