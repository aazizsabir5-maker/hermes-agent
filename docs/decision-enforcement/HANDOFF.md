# Fresh-Session Handoff

Use this document when continuing the fork in a new chat, with a new agent, or after context loss.

## Copy-paste brief

```text
Repository: /Users/ariansabir/Developer/hermes-agent-enforced
Fork: https://github.com/aazizsabir5-maker/hermes-agent

Read these tracked files completely before proposing or making changes:
1. NORTH_STAR.md
2. docs/decision-enforcement/PRODUCT-DECISIONS.md
3. docs/decision-enforcement/CURRENT-STATE.md
4. docs/decision-enforcement/CORRECTION-PLAN.md
5. docs/decision-enforcement/HANDOFF.md
6. skills/design/comprehensive-designer-cognition/SKILL.md
7. docs/design-enforcement.md as legacy strict-architecture context
8. AGENTS.md for repository contribution rules

North Star:
Make `hermes 1` reliably apply the comprehensive hierarchical design-decision philosophy without requiring the user to operate modes, manifests, receipts, snapshots, reviewer sessions, reconciliation, or other backend stages.

Single enforceable rule:
Before Hermes may claim a substantial design is finished, every consequential in-scope decision must be traceable from intent to implementation and must record its alternatives, selected direction, tradeoff, evidence or assumption, downstream consequence, validation status, and reopening condition; unresolved consequential decisions must be disclosed as unresolved rather than silently treated as complete.

Current situation:
The existing strict fork works on its covered local path, but it changes 65 files and adds roughly 6,949 lines relative to its original base. It requires working/finalizing modes, a ten-file completion package, immutable reviewer snapshots, process-local HMAC receipts, session binding, reconciliation, and cross-surface response hardening. This exceeds the intended product.

Approved direction to review/plan:
- Keep `hermes 1`, mandatory skill injection, hierarchical decision discipline, one observable decision ledger, proportionate evidence, and a narrow completion-claim gate.
- Remove default manual modes, `.hermes/enforcement.json`, mandatory trusted review, process receipts, immutable snapshots, session choreography, ten mandatory files, and strict cross-surface design-delivery machinery.
- Make independent review and rich evidence proportional or optional.
- Use one `DESIGN-DECISIONS.md` ledger.
- The user should work normally and say “Finish this project”; Hermes handles the internal check.
- Do not keep strict and lean systems as permanent parallel modes.

Honest guarantee:
For substantial design work launched with `hermes 1`, Hermes loads the comprehensive decision philosophy, records consequential decisions in an observable ledger, and blocks its own completion claim when that ledger lacks required decision evidence.

Non-claims:
Do not claim proof of private cognition, objective design quality, evidence truth, reviewer intelligence, production readiness beyond the stated fidelity, or tamper-proof delivery across every Hermes surface.

Implementation discipline:
- Use strict TDD: failing test first, verify RED, minimal implementation, verify GREEN.
- Compare against current upstream before reverting strict-enforcement hunks; preserve newer upstream fixes.
- Every retained production hunk must map to the single invariant or `hermes 1` user experience.
- Run focused tests, relevant core regressions, canonical scripts/run_tests.sh, Ruff, compile checks, and git diff --check.
- Obtain independent philosophy-fidelity and maintainability/footprint reviews.
- Remediate all blocking findings and rerun reviews.
- Report a final complexity budget.
- Do not merge or publish until explicitly requested and verified.

User experience target:
1. cd /path/to/project
2. hermes 1
3. describe the design task normally
4. say “Finish this project”
No other user-managed stages.
```

## Before editing

Run read-only discovery:

```bash
cd /Users/ariansabir/Developer/hermes-agent-enforced
git status --short --branch
git remote -v
git log --oneline -10
git fetch upstream
git diff --stat upstream/main...HEAD
```

Then inspect current upstream versions of every core file that the correction may revert. The original strict fork was based on an older upstream commit; blind reverts can discard newer Hermes fixes.

## Authoritative product decisions

### Product

- One maintained fork.
- One enforced launcher: `hermes 1`.
- Plain `hermes` remains ordinary Hermes.
- One universal decision ledger.
- Zero user-managed backend stages.
- One-way migration from the legacy strict protocol.

### Philosophy

- Design is a hierarchy/graph of decisions.
- Consequential upstream decisions precede dependent details.
- Alternatives and tradeoffs make choices visible.
- Evidence is distinguished from assumptions.
- Decisions propagate consequences.
- Validation is proportional to claim and risk.
- Reality can reopen upstream choices.
- Completion is fidelity-qualified and scope-bound.

### Enforcement

- Skill injection is mandatory on the `hermes 1` path.
- Working and exploratory responses remain usable.
- Only an attempted substantial-design completion claim triggers the ledger gate.
- Missing evidence yields concise, decision-specific feedback.
- The gate validates observable structure, not semantic truth or private cognition.

### Optional by risk

- independent review;
- screenshots and perceptual audits;
- artifact hashing;
- adversarial review;
- richer specifications and validation reports.

### Remove from the default product

- manual `working`/`finalizing` modes;
- `.hermes/enforcement.json`;
- `design_review_request` as a universal requirement;
- process-local HMAC receipts;
- reviewer/session binding;
- immutable snapshots;
- forced reconciliation;
- ten mandatory protocol documents;
- design-specific gateway/cron/proxy/media restrictions;
- user-facing policy IDs and audit internals.

## Required implementation order

Follow `CORRECTION-PLAN.md`. In summary:

1. Lock the lean behavior with failing tests.
2. Reduce the skill’s mandatory completion contract.
3. Replace the large validator with a one-ledger validator.
4. Make enforcement automatic and mode-free.
5. Make `hermes 1` a durable tracked launcher.
6. Remove strict cross-surface and provenance machinery cluster by cluster.
7. Add one-way migration for existing projects.
8. Rewrite user documentation.
9. Run full validation and two independent reviews.
10. Publish one corrected fork state only after approval.

Do not begin by deleting files. Tests must define the target behavior first.

## Acceptance scenarios

The final implementation must demonstrate:

1. In a blank writable project, `hermes 1` starts enforced design work without another setup command.
2. Hermes creates one decision ledger automatically.
3. Normal exploration is not blocked.
4. A claimed completion with no ledger is blocked with a specific explanation.
5. A committed consequential decision lacking a selected direction, alternatives/tradeoff/evidence/consequence/validation/reopening information blocks completion; omission of each field is tested independently.
6. A consequential decision without a trace from intent and selection to a concrete project-relative artifact or representation blocks completion at fidelities that require realization.
7. A missing, out-of-root, or nonexistent local artifact reference blocks completion; structural reference validation does not claim semantic correctness.
8. An unresolved in-scope consequential decision blocks even an otherwise valid fidelity-qualified completion claim, and every unresolved decision ID is surfaced directly.
9. Provisional or “ready for next commitment” language remains allowed.
10. A structurally valid ledger with fidelity-appropriate realization references allows a fidelity-qualified completion statement.
11. Restarting Hermes does not invalidate the ledger or require review-session choreography.
12. Plain `hermes` is unaffected.
13. Existing strict-protocol projects can migrate once without invented content or silent data loss.

## Complexity budget

Report these before merge:

- number of production files changed relative to current upstream;
- net added lines;
- mandatory user commands;
- user-managed stages;
- mandatory project artifacts;
- runtime state directories;
- legacy files removed;
- focused and full-suite results.

Targets:

- one command: `hermes 1`;
- zero user-managed stages;
- one mandatory project artifact;
- zero receipt/snapshot directories;
- materially fewer changes than the strict 65-file/~6,949-line implementation.

## Current known external state

- Machine-local `hermes 1` wrapper exists at `/Users/ariansabir/.local/bin/hermes`.
- It points to `/Users/ariansabir/Developer/hermes-agent-enforced/.venv/bin/hermes --profile decision`.
- The wrapper source is not yet tracked in this repository; the correction plan must make it reproducible.
- The strict `exitn` project exists at `/Users/ariansabir/Desktop/exitn` and can inform migration fixtures, but do not modify or archive it without explicit user approval.
- Credentials may exist in the surrounding Hermes environment. Never copy credentials, auth files, environment values, or secret-bearing logs into fixtures or documentation.

## If asked to remove something

Before removal:

1. Map it to the North Star and single invariant.
2. Identify its callers, tests, and upstream counterpart.
3. Write or preserve behavior-contract tests.
4. Remove one cluster at a time.
5. Run focused regressions after each cluster.
6. Confirm the deletion does not weaken the honest product claim beyond what the North Star already approves.

## If asked to add something

Require a direct answer to:

- Which part of the single rule does it enforce?
- Why can the skill or ledger not handle it?
- Does it add a command, mode, file, state directory, or recovery step?
- Is it proportional to the risk?
- Does it recreate strict-provenance complexity under another name?

Reject speculative backend machinery that lacks a concrete North-Star requirement.

## If the documents disagree

Use this precedence:

1. `NORTH_STAR.md`
2. `docs/decision-enforcement/PRODUCT-DECISIONS.md`
3. `docs/decision-enforcement/CORRECTION-PLAN.md`
4. `docs/decision-enforcement/CURRENT-STATE.md`
5. bundled skill
6. legacy strict implementation/docs

Treat legacy conflicts as planned correction work.
