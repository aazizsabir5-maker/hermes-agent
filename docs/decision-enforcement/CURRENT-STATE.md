# Current State and Architectural Context

## Purpose of this document

This document records the repository state and history needed to continue work without access to the original chat. It distinguishes the implemented strict system from the approved direction proposed in the North Star and correction plan.

## Repository identity

- Fork repository: `https://github.com/aazizsabir5-maker/hermes-agent`
- Local checkout: `/Users/ariansabir/Developer/hermes-agent-enforced`
- Upstream repository: `https://github.com/NousResearch/hermes-agent`
- Maintained branch before the documentation work: `main`
- Strict-enforcement `main` merge commit at this handoff: `c63469c0db9e1c0fe5f49277f5e5d2ba34c25aaf`
- Documentation branch: `docs/decision-enforcement-north-star`
- Original upstream base used for the first strict implementation: `10b388300a63d83857fac3ca4f8b05b64e01bc50`

Commit identifiers are historical orientation, not permanent sources of truth. Always inspect the current branch and remotes before implementation.

## User entry points

The machine-local launcher is:

```text
/Users/ariansabir/.local/bin/hermes
```

It currently behaves as follows:

- `hermes` launches the standard installation at `/Users/ariansabir/.hermes/hermes-agent/venv/bin/hermes`.
- `hermes 1` launches the maintained fork at `/Users/ariansabir/Developer/hermes-agent-enforced/.venv/bin/hermes --profile decision`.

Verified strict-fork state before this documentation branch:

- fork version: Hermes Agent v0.20.6;
- `design-enforcement` plugin toolset enabled;
- plain `hermes` remains on the separate standard installation.

The launcher modification is currently machine-local. The correction plan requires a tracked launcher/installer source so the repository itself documents and reproduces this behavior.

## Original objective

The original objective was to make Hermes reliably apply the `comprehensive-designer-cognition` philosophy to design work. The key idea was simple:

- treat design as a hierarchy of consequential decisions;
- resolve upstream choices before dependent details;
- compare meaningful alternatives;
- name tradeoffs, assumptions, and downstream consequences;
- validate in proportion to risk;
- reopen decisions when evidence disagrees;
- avoid unsupported claims of completion.

The fork was created because prompt guidance alone could be ignored or weakened. A trusted runtime boundary was added to prevent the model from claiming completion without satisfying the design protocol.

## What was implemented

The strict implementation added a generic required-finalization policy system and a bundled `design_enforcement` policy. It currently includes:

1. Turn-start policy applicability and project-required policy freezing.
2. Candidate-response buffering for applicable required-policy turns.
3. Release gating before persistence and delivery.
4. A large deterministic completion manifest and validator.
5. A trusted `design_review_request` tool.
6. Content-addressed immutable review snapshots.
7. A read-only reviewer child with constrained tools.
8. Runtime-authenticated, process-local HMAC receipts.
9. Parent-session, reviewer-session/model, subject-hash, report-hash, and validator binding.
10. Freshness rechecks before release.
11. Durable finalization audit records.
12. Exact approved-response or host-blocked-response behavior.
13. Protections across streaming, callbacks, persistence, gateway, API, cron, background, proxy, Codex, media rewriting, early exits, errors, truncation, and invalid-tool exhaustion.
14. Protected bundled policy registration that cannot be disabled, shadowed, or publicly unloaded.
15. CLI refusal of `--safe-mode` and `--ignore-rules` for enforced projects.

## Current strict workflow

The implemented workflow requires:

1. Initialize protocol files.
2. Keep project mode `working` while building.
3. Maintain eight builder-owned protocol files.
4. Include actual implementation and evidence as manifest-bound attachments.
5. Reset review and completion fields to pre-review state.
6. Invoke `design_review_request` directly in the current Hermes process.
7. Obtain a passing reviewer result and process-local trusted receipt.
8. Reconcile post-review manifest fields.
9. Run final deterministic validation.
10. Change the project to `finalizing` mode.
11. Make a fidelity-qualified completion claim in the same process and session.

This workflow was eventually proven to work, but it required too much user knowledge and too many recoveries.

## Successful strict-finalization evidence

A successful enforced finalization was recorded for `/Users/ariansabir/Desktop/exitn` in session `20260828_094032_6fc61b`.

The runtime audit recorded:

- `decision: allow`;
- `reason_code: design_completion_passed`;
- `mode: finalizing`;
- `trusted_review: true`;
- `validator_exit_code: 0`;
- canonical subject and report hashes;
- fidelity-qualified completion text with limitations preserved.

This proves that the strict implementation can function on its covered local path. It does not prove objective design quality, evidence truth, or private cognition.

## Operational failures that exposed product mismatch

The `exitn` trial revealed several sources of complexity:

### Ordinary review was not trusted

An early review used `delegate_task`, producing a project receipt but no runtime-trusted receipt. Finalization correctly blocked with `trusted_review_missing_or_stale`.

### Reviewer recursion

The trusted reviewer’s immutable snapshot contained the project enforcement configuration. The reviewer prompt itself matched the design policy, causing the reviewer child to enter the same completion policy recursively and block its own report.

This was fixed in PR 5 by marking only host-created, profile-snapshot, exact-`file-readonly` reviewer children as trusted review sessions and skipping parent finalization policy recursion for those children. Independent review found no blocking defect in that fix.

### Missing implementation evidence

A trusted reviewer initially saw only protocol documents, not the homepage, brand guide, CSS, JavaScript, SVGs, screenshots, and browser-audit programs. It correctly failed the review. The manifest was expanded to bind those files as attachments.

### Process and session mismatch

The active Hermes session did not expose the trusted tool. The agent launched another Hermes process through `terminal`/`process`, creating a valid receipt for the wrong process and parent session. Finalization in the original session correctly rejected it.

### Dynamic-tool wrapper mismatch

Instructions later referred to `tool_describe` and `tool_call`, but the classic CLI exposed the plugin tool directly rather than exposing those dynamic wrappers. A fresh fork process was required before `design_review_request` appeared as a direct first-class tool.

### User-visible mode transition

The user had to understand `working`, pre-review state, trusted review, reconciliation, deterministic validation, `finalizing`, process lifetime, and session identity. This contradicted the original desire to enforce a design philosophy simply.

These were not merely documentation failures. They show that the backend product being operated was larger than the user’s intended product.

## Current code footprint

Relative to the original upstream base, the strict fork changes 65 files and adds approximately 6,949 lines while removing approximately 275 lines.

Major production areas touched include:

- `agent/agent_init.py`
- `agent/chat_completion_helpers.py`
- `agent/conversation_loop.py`
- `agent/finalization_gate.py`
- `agent/finalization_policy.py`
- `agent/subagent_lifecycle.py`
- `agent/system_prompt.py`
- `agent/turn_context.py`
- `agent/turn_finalizer.py`
- `run_agent.py`
- `cron/scheduler.py`
- `gateway/platforms/api_server.py`
- `gateway/run.py`
- `hermes_cli/main.py`
- `hermes_cli/plugins.py`
- `toolsets.py`
- `plugins/policies/design_enforcement/*`

The bundled skill currently includes:

- a long mandatory completion contract;
- eight builder templates;
- independent-review prompt/report/receipt templates;
- initializer, validator, and receipt helper scripts.

The test suite includes policy, release gate, stream buffering, persistence, reviewer, snapshot, receipt, validator, plugin, gateway, cron, proxy, toolset, CLI bypass, and exhaustion coverage.

## Important strict-system files

### Generic runtime

- `agent/finalization_policy.py`
- `agent/finalization_gate.py`
- `agent/turn_context.py`
- `agent/turn_finalizer.py`
- `run_agent.py`

### Design policy

- `plugins/policies/design_enforcement/__init__.py`
- `plugins/policies/design_enforcement/policy.py`
- `plugins/policies/design_enforcement/reviewer.py`
- `plugins/policies/design_enforcement/review_snapshot.py`
- `plugins/policies/design_enforcement/receipt.py`
- `plugins/policies/design_enforcement/validator_runner.py`

### Skill and validator

- `skills/design/comprehensive-designer-cognition/SKILL.md`
- `skills/design/comprehensive-designer-cognition/scripts/init_design_protocol.py`
- `skills/design/comprehensive-designer-cognition/scripts/validate_design_completion.py`
- `skills/design/comprehensive-designer-cognition/templates/*`

### Documentation and tests

- `docs/design-enforcement.md`
- `tests/agent/test_finalization_gate.py`
- `tests/agent/test_finalization_policy.py`
- `tests/agent/test_project_required_policies.py`
- `tests/plugins/test_design_*.py`
- `tests/run_agent/test_required_policy_stream_buffer.py`
- `tests/hermes_cli/test_required_policy_bypass.py`
- `tests/hermes_cli/test_trusted_policy_plugin_shadowing.py`

## Published strict-enforcement history

The fork’s strict implementation was published through these pull requests:

1. PR 1 — initial fail-closed design finalization implementation.
2. PR 2 — early-return, callback, persistence, reasoning, tool-call, gateway, and exhaustion hardening.
3. PR 3 — quick-start enforcement configuration and initializer behavior.
4. PR 4 — corrected skill guidance to require the trusted review tool.
5. PR 5 — trusted reviewer policy-recursion fix.

The exact commit graph should be inspected before new work. Do not assume historical SHAs are the current merge base.

## Corrected target architecture

The North Star and correction plan propose:

1. `hermes 1` marks the session as decision-enforced.
2. The comprehensive skill is loaded automatically.
3. One `DESIGN-DECISIONS.md` ledger is created and maintained automatically.
4. Exploratory and working responses are allowed normally.
5. An attempted substantial-design completion claim triggers one small ledger validator.
6. A valid ledger allows a fidelity-qualified claim.
7. An invalid ledger returns specific unresolved decision IDs and continues work.
8. Independent review, artifact hashes, richer audits, and supporting evidence are proportional or optional—not universal ceremony.
9. No manual modes, receipts, snapshots, session binding, or reconciliation.
10. Plain `hermes` remains unaffected.

## Migration constraint

Do not preserve the strict and lean protocols as two permanent modes. That would recreate the backend drift the correction is intended to eliminate.

Provide one tested migration from legacy protocol files to `DESIGN-DECISIONS.md`. Leave old files untouched or archive them only with user approval. New projects should use only the lean contract.

## Security and honesty boundary

The corrected product deliberately gives up strict process-local provenance and universal release hardening. It must say so plainly.

The retained guarantee is observable design-decision discipline and a completion-claim check for the `hermes 1` path. Do not continue advertising strict cross-surface anti-bypass guarantees after removing the machinery that supported them.

## Immediate next decision

Before implementation, confirm this tradeoff:

> Choose simple, observable enforcement of comprehensive design decisions over strict process-local reviewer provenance and universal response-release security.

The user requested this simplification direction and a self-contained review/correction package. The specific lean architecture remains a proposal until the implementation approval checkpoint in `CORRECTION-PLAN.md` is accepted. Any implementation still requires explicit execution approval, TDD, independent review, and a complexity-budget report before merge.
