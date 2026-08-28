# Fresh-Session Handoff

## Copy-paste brief

```text
Repository: /Users/ariansabir/Developer/hermes-agent-enforced
Fork: https://github.com/aazizsabir5-maker/hermes-agent
Working branch at handoff: refactor/lean-decision-enforcement

Read completely, in order:
1. NORTH_STAR.md
2. DESIGN-DECISIONS.md
3. docs/decision-enforcement/PRODUCT-DECISIONS.md
4. docs/decision-enforcement/CURRENT-STATE.md
5. docs/decision-enforcement/CORRECTION-PLAN.md
6. docs/decision-enforcement/HANDOFF.md
7. docs/design-enforcement.md
8. skills/design/comprehensive-designer-cognition/SKILL.md
9. AGENTS.md

North Star:
Make `hermes 1` reliably apply the comprehensive hierarchical design-decision philosophy without user-managed modes, manifests, receipts, snapshots, reviewer sessions, reconciliation, or backend stages.

Implemented architecture:
- hidden launcher context from tracked scripts/hermes-one;
- launch-scoped mandatory skill injection;
- one automatically created, never-overwritten DESIGN-DECISIONS.md ledger;
- one small structural validator;
- ordinary/exploratory/provisional responses allowed;
- candidate completion claims gated with actionable ledger diagnostics;
- one-way migration that leaves legacy files untouched;
- no mandatory review tool, receipt, snapshot, session binding, or project mode.

Honest guarantee:
For substantial design work launched with hermes 1, Hermes loads the comprehensive decision philosophy, records consequential decisions in an observable ledger, and blocks its own completion claim when that ledger lacks required decision evidence.

Non-claims:
No proof of private cognition, objective design quality, evidence truth, reviewer intelligence, universal tamper-proof delivery, or production readiness beyond stated fidelity.

Current verification boundary:
Implementation commits and focused RED→GREEN cycles exist. Before a completion/publication claim, rerun final focused and relevant regressions, obtain one uninterrupted canonical suite result or disclose the blocker, run clean static checks, get fresh independent philosophy and maintainability/code reviews, remediate blockers, synchronize installed launcher/profile copies, verify real commands, then publish/merge/tag as Task 10 directs.
```

## First commands

```bash
cd /Users/ariansabir/Developer/hermes-agent-enforced
git status --short --branch
git remote -v
git log --oneline -20
git diff --stat upstream/main...HEAD
```

Do not delete `DESIGN-DECISIONS.md` or these context documents. Do not restore strict and lean protocols as parallel products.

## Final focused contract

```bash
scripts/run_tests.sh \
  tests/plugins/test_lean_decision_enforcement.py \
  tests/skills/test_lean_design_decision_validator.py \
  tests/skills/test_comprehensive_designer_cognition_bundle.py \
  tests/hermes_cli/test_hermes_one_contract.py \
  tests/skills/test_design_protocol_migration.py -q
```

Relevant core regressions include finalization policy/gate, turn context/finalizer persistence, plugin prompt sections/registration, launcher parsing/startup, and ordinary non-enforced conversation behavior.

## Complexity checkpoint

At the implementation checkpoint versus current `upstream/main`:

- 17 production/config/script files;
- +1,466/-11 production lines, excluding tests/docs/Markdown skill prose;
- one command;
- zero user-managed stages;
- one mandatory project artifact;
- zero receipt/snapshot runtime directories.

Recompute before publication.

## Publication order

1. Commit final repository-local context and ledger.
2. Run focused/relevant/static/canonical checks.
3. Obtain fresh independent philosophy and maintainability/code reviews.
4. Remediate every blocker and repeat affected checks/reviews.
5. Synchronize bundled skill and launcher to the explicitly requested installed paths; verify checksums/content.
6. Verify `hermes 1 --version`, `hermes 1 tools list`, and plain `hermes --version`.
7. Fast-forward fork `main`, push, tag the simplified release, and remove obsolete remote feature branches only after confirming no unique work remains.
8. Record final evidence and update `CURRENT-STATE.md` and `DESIGN-DECISIONS.md` if any result changes the claim.
