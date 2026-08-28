# Lean Decision-Philosophy Enforcement Correction Plan

> **For Hermes:** Use subagent-driven-development skill to implement this plan task-by-task.

**Goal:** Reduce the maintained fork from a multi-stage completion/provenance system to one simple, observable guarantee: substantial design work launched through `hermes 1` must follow the comprehensive hierarchical decision-making philosophy, and Hermes must not claim the work is done until a small decision contract is satisfied.

**Architecture:** Keep one maintained fork and one launcher. Preserve mandatory skill injection and a narrow completion-claim gate, but remove user-visible working/review/finalizing modes, process-local receipts, immutable-review snapshots, mandatory reviewer orchestration, ten-file manifests, and cross-surface delivery hardening that do not directly enforce the decision philosophy. Replace them with one automatically maintained `DESIGN-DECISIONS.md` ledger and one small deterministic validator invoked automatically when Hermes attempts a completion claim.

**Tech Stack:** Python 3.11, Hermes bundled-policy plugin API, pytest through `scripts/run_tests.sh`, Bash launcher at `~/.local/bin/hermes`.

---

## 1. Review conclusion

The fork currently changes 65 files and adds roughly 6,949 lines relative to its original upstream base. Most of that machinery enforces completion provenance and response-release integrity rather than the design decision philosophy itself.

### Keep

1. `hermes 1` as the single user entry point.
2. The `decision` profile and one maintained fork on `main`.
3. Mandatory loading of `comprehensive-designer-cognition` for enforced design sessions.
4. Hierarchical decision ordering: situation → intent → frame → strategy → system → experience → form → detail → realization.
5. Explicit alternatives, tradeoffs, assumptions, consequences, validation, and reopening conditions for consequential decisions.
6. A narrow host-side check preventing an unsupported completion claim.
7. Clear distinction between facts, assumptions, preferences, and commitments.
8. Fidelity-qualified language rather than unqualified “complete.”

### Remove from the default enforced workflow

1. Manual `working` and `finalizing` modes.
2. `.hermes/enforcement.json` as a per-project mode switch.
3. User-managed review and reconciliation stages.
4. Mandatory `design_review_request` for ordinary enforced design work.
5. Process-local HMAC receipts and parent-session binding.
6. Immutable snapshot directories and reviewer-only filesystem toolsets.
7. Mandatory reviewer report and receipt files.
8. The eight builder documents plus two reviewer documents as a universal requirement.
9. Exact candidate/released response hashing for this design policy.
10. Design-policy restrictions across gateways, cron, ACP, proxy, API media rewriting, Codex app-server, and unrelated delivery surfaces.
11. Generic blocked prose that hides the actual missing decision evidence.
12. User instructions involving session IDs, `/new`, process restarts, receipt freshness, reconciliation, or mode transitions.

### Make optional rather than mandatory

1. Independent review for high-risk, expensive, public, safety-relevant, or user-requested work.
2. Rich design briefs, system specifications, perceptual audits, screenshots, and implementation test evidence when appropriate to the design commitment.
3. Artifact hashing when freshness or handoff integrity materially matters.
4. Adversarial runtime release enforcement for users who explicitly choose a future “strict provenance” product, if that product is retained at all.

## 2. Reduced trust claim

The corrected fork should claim only:

> For substantial design work launched with `hermes 1`, Hermes loads the comprehensive decision philosophy, records consequential decisions in an observable ledger, and blocks its own completion claim when that ledger lacks required decision evidence.

It must explicitly not claim to prove:

- private model cognition;
- objective design quality;
- truth of evidence;
- reviewer intelligence or independence;
- production readiness;
- tamper-proof delivery across every Hermes surface.

This reduction is intentional. It aligns the implementation with the original objective instead of preserving a larger security/provenance product that the user did not request.

## 3. Target user experience

### Start

```bash
cd /path/to/project
hermes 1
```

### Work

The user describes the design task normally. Hermes automatically applies the decision philosophy and maintains one ledger. No initialization command, mode toggle, review command, or validator command is exposed to the user.

### Finish

The user can say any ordinary equivalent of:

```text
Finish this project.
```

Hermes automatically checks the decision ledger. It either:

- finishes with a fidelity-qualified statement; or
- gives a short, specific list of unresolved decisions and continues working.

The user should never need to know about policy IDs, manifests, hashes, receipts, snapshots, session identity, or backend stages.

## 4. Single enforceable rule

Use this as the policy invariant:

> Before Hermes may claim a substantial design is finished, every consequential in-scope decision must be traceable from intent to implementation and must record its alternatives, selected direction, tradeoff, evidence or assumption, downstream consequence, validation status, and reopening condition; unresolved consequential decisions must be disclosed as unresolved rather than silently treated as complete.

This rule directly represents the philosophy. Everything retained in the backend must trace to this invariant.

---

## 5. Implementation tasks

### Task 1: Lock the reduced product contract with tests

**Objective:** Establish failing tests for the simple user experience before changing production code.

**Files:**
- Create: `tests/plugins/test_lean_decision_enforcement.py`
- Create: `tests/hermes_cli/test_hermes_one_contract.py`
- Modify later: `plugins/policies/design_enforcement/__init__.py`
- Modify later: `plugins/policies/design_enforcement/policy.py`

**Step 1: Write failing launcher-contract tests**

Test that an enforced launch:

- activates the decision policy without `.hermes/enforcement.json`;
- requires no manual mode;
- exposes no review/finalization lifecycle instructions in the system prompt;
- works from any writable project directory.

**Step 2: Write failing decision-policy tests**

Test these behaviors independently:

1. Non-design conversation: policy does not interfere.
2. Exploratory design response without a completion claim: allowed.
3. Completion claim with no ledger: blocked with a specific missing-ledger message.
4. Completion claim with unresolved consequential decisions: blocked with their IDs.
5. Completion claim with a valid ledger: allowed.
6. “Ready for next iteration” or “provisional” language: allowed when unresolved decisions remain.
7. No receipt, snapshot, reviewer session, or mode field is required.

**Step 3: Verify RED**

Run:

```bash
scripts/run_tests.sh \
  tests/plugins/test_lean_decision_enforcement.py \
  tests/hermes_cli/test_hermes_one_contract.py -q
```

Expected: failures because the current policy still requires modes, validator manifests, and trusted receipts.

**Step 4: Commit tests**

```bash
git add tests/plugins/test_lean_decision_enforcement.py tests/hermes_cli/test_hermes_one_contract.py
git commit -m "test: define lean decision enforcement contract"
```

### Task 2: Reduce the skill to philosophy plus one observable contract

**Objective:** Preserve comprehensive hierarchical decision-making while removing mandatory backend ceremony from the default workflow.

**Files:**
- Modify: `skills/design/comprehensive-designer-cognition/SKILL.md`
- Modify: `/Users/ariansabir/.hermes/profiles/decision/skills/design/comprehensive-designer-cognition/SKILL.md` only after the bundled version passes review
- Create: `skills/design/comprehensive-designer-cognition/templates/DESIGN-DECISIONS.md`
- Delete after migration: the mandatory completion templates listed in Task 7
- Test: `tests/skills/test_comprehensive_designer_cognition_bundle.py`

**Step 1: Write failing skill assertions**

Require the bundled skill to state:

- the single enforceable rule verbatim;
- progressive decision expansion;
- consequential-decision fields;
- one-ledger behavior;
- proportionate evidence;
- optional independent review based on risk;
- no mandatory working/finalizing mode;
- no mandatory receipt or session choreography.

**Step 2: Verify RED**

```bash
scripts/run_tests.sh tests/skills/test_comprehensive_designer_cognition_bundle.py -q
```

**Step 3: Rewrite only the completion section**

Keep the existing core model, hierarchy, procedure, critique, validation principles, and communication rules. Replace Gates A–K and the ten mandatory files with:

- one completion invariant;
- one `DESIGN-DECISIONS.md` ledger for substantial writable-project work;
- proportionate optional supporting artifacts;
- optional independent review based on consequence/risk;
- fidelity-qualified completion language.

**Step 4: Define the ledger template**

Minimum sections:

```markdown
# Design Decisions

## Boundary
- Design object
- Intended effect
- In scope
- Out of scope
- Target fidelity

## Decision map
- D-001 [status] parent → child relationship

## Consequential decisions
### D-001 — Name
- Level
- Question
- Criteria
- Alternatives
- Selection
- Tradeoff
- Evidence
- Assumptions
- Consequences
- Realization status
- Artifact references
- Validation
- Reopen if

## Unresolved consequential decisions

## Completion status
- Fidelity
- Supported claim
- Known limitations
```

**Step 5: Verify GREEN and commit**

```bash
scripts/run_tests.sh tests/skills/test_comprehensive_designer_cognition_bundle.py -q
git add skills/design/comprehensive-designer-cognition tests/skills/test_comprehensive_designer_cognition_bundle.py
git commit -m "refactor: reduce design protocol to one decision contract"
```

### Task 3: Replace the large validator with a small decision-ledger validator

**Objective:** Validate only the observable evidence needed by the single decision rule.

**Files:**
- Replace: `skills/design/comprehensive-designer-cognition/scripts/validate_design_completion.py`
- Replace: `skills/design/comprehensive-designer-cognition/scripts/init_design_protocol.py`
- Delete: `skills/design/comprehensive-designer-cognition/scripts/create_review_receipt.py`
- Create or replace tests: `tests/skills/test_lean_design_decision_validator.py`

**Step 1: Write a smallest honest passing fixture**

Create one ledger with:

- a bounded design object;
- one intent;
- one parent and one child decision;
- one complete consequential record;
- one trace from the parent intent through the selected decision to a concrete in-scope artifact or representation appropriate to the target fidelity;
- no unresolved consequential decision;
- a fidelity-qualified supported claim.

**Step 2: Write one-mutation negative fixtures**

Require controlled failure for:

- missing ledger;
- missing boundary;
- committed decision without a record;
- missing meaningful alternative without a stated “no credible alternative” reason;
- missing tradeoff;
- missing evidence/assumption distinction;
- missing consequence;
- missing realization status;
- missing artifact/reference trace from intent through selection to the realized design;
- local artifact reference that does not exist, is absolute, or resolves outside the project root (including symlink escape);
- a decision marked “not yet realized” combined with a completion claim whose fidelity requires that realization;
- missing validation status;
- missing reopening condition;
- unresolved consequential decision combined with an unqualified completion claim;
- malformed UTF-8 or malformed structure.

**Step 3: Verify RED**

```bash
scripts/run_tests.sh tests/skills/test_lean_design_decision_validator.py -q
```

**Step 4: Implement the minimal validator**

Required properties:

- reads one `DESIGN-DECISIONS.md` file;
- requires each consequential decision to state whether and how it is realized at the target fidelity;
- requires project-relative artifact or representation references that connect the selected decision to observable output, and verifies that local references exist beneath the project root;
- permits “not yet realized” only when the supported claim is explicitly below the fidelity that would require realization;
- produces concise actionable diagnostics;
- has no receipt, snapshot, session, HMAC, project-mode, or binary-evidence logic;
- does not claim to judge the quality or truth of decisions;
- exits `0` only when the observable decision contract is structurally satisfied.
- does not infer that an artifact reference proves semantic correctness; it verifies trace structure, reference scope, and local existence only.

**Step 5: Simplify initialization**

The initializer should create only `DESIGN-DECISIONS.md` when absent. The agent/plugin may invoke it automatically; the user should not need to run it.

**Step 6: Verify and commit**

```bash
scripts/run_tests.sh tests/skills/test_lean_design_decision_validator.py -q
git add skills/design/comprehensive-designer-cognition/scripts tests/skills/test_lean_design_decision_validator.py
git commit -m "refactor: validate one design decision ledger"
```

### Task 4: Make enforcement automatic and mode-free

**Objective:** Eliminate user-managed stages while retaining a narrow completion-claim gate.

**Files:**
- Modify: `plugins/policies/design_enforcement/__init__.py`
- Replace: `plugins/policies/design_enforcement/policy.py`
- Modify or remove if no longer needed: `plugins/policies/design_enforcement/validator_runner.py`
- Delete after tests move: `plugins/policies/design_enforcement/receipt.py`
- Delete after tests move: `plugins/policies/design_enforcement/review_snapshot.py`
- Delete after tests move: `plugins/policies/design_enforcement/reviewer.py`
- Modify: `plugins/policies/design_enforcement/plugin.yaml`
- Tests: `tests/plugins/test_lean_decision_enforcement.py`

**Step 1: Verify the Task 1 policy tests remain RED**

**Step 2: Replace applicability logic**

The policy applies when both are true:

- the process was launched through the `hermes 1` enforced entry point; and
- the current request is a substantial design task or attempts a design completion claim.

Do not read `.hermes/enforcement.json` and do not expose a mode.

**Step 3: Auto-create the ledger**

At the first substantial design turn in a writable project, create the ledger only if absent. Never overwrite it.

**Step 4: Narrow the release gate**

- Exploratory and working responses are not blocked.
- A candidate completion claim triggers the small ledger validator.
- Pass releases the fidelity-qualified claim.
- Failure returns a concise host-authored explanation listing missing or unresolved decision evidence.
- The response should say “not yet complete” rather than emit a generic policy error.

**Step 5: Remove the review tool from the default plugin**

Delete `design_review_request` registration. Independent review becomes an ordinary optional agent action chosen by risk or requested by the user, not a required provenance token.

**Step 6: Verify GREEN and commit**

```bash
scripts/run_tests.sh tests/plugins/test_lean_decision_enforcement.py -q
git add plugins/policies/design_enforcement tests/plugins/test_lean_decision_enforcement.py
git commit -m "refactor: enforce decisions without lifecycle modes"
```

### Task 5: Make `hermes 1` the complete entry point

**Objective:** Ensure the user never chooses a fork, profile, plugin, or stage.

**Files:**
- Create in repo: `scripts/hermes-one`
- Modify local launcher during installation: `/Users/ariansabir/.local/bin/hermes`
- Test: `tests/hermes_cli/test_hermes_one_contract.py`
- Document: `docs/design-enforcement.md`

**Step 1: Add failing launcher tests**

Assert that `hermes 1 --version` resolves to this fork and that the launched environment marks the session as decision-enforced without requiring a project config file.

**Step 2: Add a durable launcher marker**

The wrapper should pass one internal, non-user-facing launch marker to the fork. Prefer a CLI argument or config-backed launch context over a public non-secret environment variable.

**Step 3: Keep one path**

`hermes 1` must always execute:

```text
/Users/ariansabir/Developer/hermes-agent-enforced/.venv/bin/hermes --profile decision
```

Plain `hermes` remains unchanged.

**Step 4: Fail clearly if the fork is missing**

Return one copyable repair command rather than silently falling back to stock Hermes.

**Step 5: Verify**

```bash
hermes 1 --version
hermes 1 tools list
hermes --version
```

Expected:

- `hermes 1`: maintained fork, decision policy enabled;
- `hermes`: standard installation unchanged.

**Step 6: Commit the durable installer/launcher source**

```bash
git add scripts/hermes-one tests/hermes_cli/test_hermes_one_contract.py docs/design-enforcement.md
git commit -m "feat: make hermes one the enforced design entry point"
```

### Task 6: Remove cross-surface and provenance overengineering

**Objective:** Delete code that no longer traces to the reduced local `hermes 1` guarantee.

**Files to review and revert toward upstream where the only reason for modification was strict design finalization:**

- `agent/chat_completion_helpers.py`
- `agent/conversation_loop.py`
- `agent/subagent_lifecycle.py`
- `cron/scheduler.py`
- `gateway/platforms/api_server.py`
- `gateway/run.py`
- `run_agent.py`
- `toolsets.py`
- corresponding gateway, subagent, stream-buffer, proxy, and background tests

**Files to keep only if the lean completion gate still requires them:**

- `agent/finalization_policy.py`
- `agent/finalization_gate.py`
- `agent/turn_context.py`
- `agent/turn_finalizer.py`
- `agent/agent_init.py`
- `agent/system_prompt.py`
- `hermes_cli/plugins.py`

**Step 1: Build a requirement-to-diff matrix**

For every changed production hunk relative to the chosen current upstream base, label it:

- required for mandatory skill injection;
- required for completion-claim ledger validation;
- generic upstream-worthy finalization support;
- legacy strict-provenance machinery;
- unrelated carried change.

No hunk may remain unlabeled.

**Step 2: Write regression tests before each removal cluster**

The lean positive/negative behavior must remain green while strict-provenance-only tests are intentionally deleted or rewritten.

**Step 3: Remove one cluster at a time**

Recommended order:

1. reviewer lifecycle and `file-readonly` special case;
2. receipt and snapshot support;
3. gateway/proxy/Codex prohibitions;
4. cron/background/media special handling;
5. provider-error and exhaustive early-return redaction used only by universal buffering;
6. trusted-policy unload/shadow restrictions that are unnecessary once the plugin is an ordinary bundled policy;
7. project-required policy parsing if no other consumer exists.

**Step 4: Rebase comparisons onto current upstream**

Do not blindly revert to the old `10b3883` base. Fetch current upstream and compare each file so current Hermes fixes are preserved.

**Step 5: Commit each removal cluster separately**

Example:

```bash
git commit -m "refactor: remove trusted reviewer lifecycle"
git commit -m "refactor: remove cross-surface design buffering"
```

### Task 7: Remove legacy project ceremony and provide one migration

**Objective:** Avoid two competing protocols or multiple backend stages.

**Delete from the default skill after migration support is tested:**

- `templates/ORIGINAL-REQUEST.md`
- `templates/DESIGN-BRIEF.md`
- `templates/DECISION-MAP.md`
- `templates/DECISION-RECORDS.md`
- `templates/SYSTEM-SPEC.md`
- `templates/DESIGN-AUDIT.md`
- `templates/VALIDATION-REPORT.md`
- `templates/DESIGN-COMPLETION.json`
- `templates/INDEPENDENT-REVIEW-PROMPT.md`
- `templates/INDEPENDENT-REVIEW.md`
- `templates/REVIEW-RECEIPT.json`
- `templates/enforcement.json`
- `templates/project.hermes.md` if its only purpose is the legacy contract

**Files:**
- Create: `skills/design/comprehensive-designer-cognition/scripts/migrate_to_decision_ledger.py`
- Test: `tests/skills/test_design_protocol_migration.py`

**Step 1: Write a failing migration test using the current `exitn` fixture shape**

The migration must:

- read old decision map and records;
- produce one `DESIGN-DECISIONS.md` without inventing decisions;
- preserve scope, fidelity, unresolved items, and reopening conditions;
- leave old files untouched by default;
- report which files are now legacy.

**Step 2: Implement one-way migration**

No dual-write and no permanent compatibility mode. Existing projects can be migrated once; new projects use only the ledger.

**Step 3: Archive, do not silently delete, user project files**

For a real project, move legacy protocol files to a user-approved archive only after the migrated ledger is reviewed. The fork should stop requiring them regardless.

**Step 4: Verify and commit**

```bash
scripts/run_tests.sh tests/skills/test_design_protocol_migration.py -q
git add skills/design/comprehensive-designer-cognition tests/skills/test_design_protocol_migration.py
git commit -m "feat: migrate legacy design manifests to one ledger"
```

### Task 8: Rewrite documentation around the user’s mental model

**Objective:** Explain only what the user needs to do.

**Files:**
- Replace: `docs/design-enforcement.md`
- Modify: `README.md`
- Remove: `docs/examples/design-enforcement.json`

**Primary documentation:**

```markdown
# Enforced design decisions

1. `cd` into the project.
2. Run `hermes 1`.
3. Describe the design task normally.
4. Say “Finish this project” when ready.

Hermes records consequential decisions and will not claim completion while consequential decisions remain unresolved or untraceable.
```

Put implementation details in a separate developer section. Do not teach users about modes, receipts, snapshot hashes, reviewer sessions, audit logs, or release hashes.

**Verification:** A user unfamiliar with the fork should be able to start and finish a sample project from the first screen of documentation without asking what “finalize” means.

### Task 9: Full validation and independent review

**Objective:** Prove the simplified fork enforces the one intended rule and has actually reduced complexity.

**Step 1: Focused tests**

```bash
scripts/run_tests.sh \
  tests/plugins/test_lean_decision_enforcement.py \
  tests/skills/test_lean_design_decision_validator.py \
  tests/skills/test_comprehensive_designer_cognition_bundle.py \
  tests/hermes_cli/test_hermes_one_contract.py \
  tests/skills/test_design_protocol_migration.py -q
```

**Step 2: Relevant core regressions**

Run agent initialization, prompt construction, plugin registration, turn finalization, CLI startup, and ordinary non-enforced conversation tests.

**Step 3: Canonical suite**

```bash
scripts/run_tests.sh
```

Record honest baseline/environmental failures separately; do not call an interrupted suite a pass.

**Step 4: Static checks**

```bash
ruff check <changed-python-files>
git diff --check
python -m compileall <changed-python-directories>
```

**Step 5: Executable acceptance scenarios**

1. `hermes 1` in a blank project creates one ledger automatically.
2. A substantial design task records decisions without asking the user about backend stages.
3. An unsupported “complete” claim is blocked with actionable missing decision IDs.
4. A valid ledger allows a qualified completion claim.
5. A provisional result is allowed with unresolved decisions disclosed.
6. Plain `hermes` remains unaffected.
7. Restarting Hermes does not invalidate ordinary decision evidence or force a review ceremony.

**Step 6: Independent reviews**

Request two bounded reviews:

- philosophy fidelity: does the implementation enforce the comprehensive decision method rather than paperwork?
- maintainability/footprint: does every retained backend hunk trace to the single invariant?

Any blocking finding requires remediation and a fresh review.

**Step 7: Complexity budget**

Before merging, report:

- production files changed relative to current upstream;
- net added lines;
- number of user-visible commands/stages;
- mandatory project artifacts;
- mandatory runtime state files.

Target:

- one user command: `hermes 1`;
- zero user-managed stages;
- one mandatory project artifact;
- no receipt/snapshot directories;
- materially fewer production changes than the current 65-file, ~6,949-line fork.

### Task 10: Publish one corrected fork state

**Objective:** Avoid backend drift and competing branches.

**Step 1:** Implement on one correction branch from current fork `main`.

**Step 2:** Require all tests and independent reviews before merge.

**Step 3:** Merge to fork `main` and update the local checkout by fast-forward only.

**Step 4:** Verify `hermes 1 --version` resolves to the merged `main` checkout.

**Step 5:** Close or delete obsolete remote feature branches after confirming no unique work remains.

**Step 6:** Tag the simplified release, for example `decision-enforcement-v1`, so the launcher and documentation refer to one known state.

---

## 6. Risks and tradeoffs

### Reduced anti-bypass guarantees

Removing process receipts, immutable snapshots, and universal buffering means the fork will no longer claim tamper-resistant provenance or exact release control across every Hermes surface. This is acceptable only if the user approves the reduced claim in Section 2.

### Prompt-only limitations

The philosophy itself cannot be proven as private cognition. The retained ledger and completion gate enforce observable decision discipline, not hidden reasoning.

### Over-minimizing the ledger

One file must not become a checkbox form. Tests should require meaningful structural fields, while the skill—not the validator—governs semantic quality and proportional depth.

### Completion-claim detection

Heuristic detection can miss unusual wording. Prefer an explicit internal completion-intent signal set by the agent when it attempts a fidelity-qualified completion statement, without exposing a mode to the user. Include adversarial wording tests.

### Existing projects

Projects using the old protocol need a one-way migration. Do not maintain both systems indefinitely; that would recreate the drift this correction is intended to remove.

## 7. Approval checkpoint before implementation

Implementation should begin only after explicit agreement on this tradeoff:

> We are choosing simple, observable enforcement of comprehensive design decisions over strict process-local reviewer provenance and universal response-release security.

If approved, the correction should be executed task-by-task with TDD, independent review, and a final complexity-budget report.
