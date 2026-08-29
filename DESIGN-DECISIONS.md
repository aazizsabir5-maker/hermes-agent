# Design Decisions

## Boundary

- Design object: The maintained Hermes fork's enforced-design behavior and single `hermes 1` launcher.
- Intended effect: Apply hierarchical decision discipline automatically and block unsupported substantial-design completion claims without user-managed backend stages.
- In scope: The maintained fork's local `hermes 1` decision-enforcement path.
- Out of scope: Proof of private cognition, objective design quality, truth of evidence, mandatory reviewer provenance, universal cross-surface response security, and a permanent strict-provenance compatibility mode.
- Target fidelity: Production implementation for the local `hermes 1` CLI path and maintained fork.

## Decision map

- D-001 [validated] situation → reduced product intent
- D-002 [validated] D-001 intent → one-ledger system
- D-003 [validated] D-001 intent → mode-free completion gate
- D-004 [validated] D-003 gate → hidden launcher implementation
- D-005 [validated] D-002 system → one-way migration implementation
- D-006 [validated] D-001 intent → independent-review release realization
- D-007 [validated] D-001 intent → narrow claim-boundary implementation

## Consequential decisions

### D-001 — Enforce decision discipline rather than provenance infrastructure

- Level: Intent and Frame
- Question: What should the maintained fork primarily guarantee?
- Criteria: Direct fit to the user's objective; observable behavior; low user ceremony; maintainable footprint; honest claim boundary.
- Alternatives: Retain strict process-local provenance and universal response-release controls; reduce enforcement to observable hierarchical decisions and completion evidence.
- Selection: Reduce enforcement to the comprehensive decision philosophy, one observable ledger, and a narrow completion-claim check.
- Tradeoff: Users lose tamper-resistant reviewer provenance and universal release hardening in exchange for a simpler product aligned to the original need.
- Evidence: The approved plan documents the 65-file/~6,949-line strict footprint, operational recovery burden, and reduced trust claim; implementation commits remove strict reviewer, receipt, snapshot, project-mode, and cross-surface machinery.
- Assumptions: Observable decision records and completion discipline provide the useful guarantee the user values most.
- Consequences: Every retained backend hunk must support mandatory skill injection, ledger validation, generic finalization support, or the one-command experience.
- Validation: Focused policy, skill, validator, launcher, migration, and relevant core regression tests exercise the reduced contract; independent reviews are required before publication.
- Reopen if: The user explicitly requests a separate strict-provenance product and accepts its operational complexity.

### D-002 — Use one project decision ledger

- Level: System
- Question: What universal project evidence should substantial writable-project design work maintain?
- Criteria: Traceability from intent through consequential decisions; concise observability; automatic creation; no invented semantic truth; low artifact burden.
- Alternatives: Keep eight builder documents plus reviewer report and receipt; use one `DESIGN-DECISIONS.md` ledger with proportionate supporting artifacts.
- Selection: Use one automatically initialized `DESIGN-DECISIONS.md` containing boundary, decision map, consequential records, unresolved decisions, and qualified completion status.
- Tradeoff: A compact structural validator cannot judge semantic quality or evidence truth, so the skill and risk-proportionate review must govern depth.
- Evidence: `skills/design/comprehensive-designer-cognition/templates/DESIGN-DECISIONS.md`, the lean initializer and validator, and mutation tests define and exercise the one-file contract.
- Assumptions: Consequential decisions can be represented clearly in one Markdown ledger without requiring a universal manifest schema.
- Consequences: Legacy templates and receipt helpers are removed from the default bundle; supporting briefs, audits, screenshots, and tests remain optional when appropriate.
- Validation: The lean validator suite covers missing/malformed ledgers, missing fields, invalid alternatives, unresolved IDs, unqualified claims, and initializer non-overwrite behavior.
- Reopen if: Executable use demonstrates a consequential property that cannot be represented or referenced clearly from the ledger.

### D-003 — Gate completion claims but not exploration

- Level: Strategy and Experience
- Question: When should host-side enforcement intervene in an enforced design session?
- Criteria: Preserve fluid exploration; prevent unsupported finality; provide actionable diagnostics; avoid lifecycle modes.
- Alternatives: Buffer and gate every applicable design response; evaluate only candidate substantial-design completion claims.
- Selection: Allow ordinary, exploratory, provisional, and next-iteration responses; invoke the ledger validator only for candidate completion claims.
- Tradeoff: Heuristic completion/applicability detection can miss unusual wording and does not provide universal anti-bypass delivery guarantees.
- Evidence: `plugins/policies/design_enforcement/policy.py` and `tests/plugins/test_lean_decision_enforcement.py` cover non-design, exploratory, provisional, absent-ledger, unresolved-ledger, and valid-ledger cases.
- Assumptions: Narrow host-side detection plus mandatory skill guidance is proportionate to the stated local CLI guarantee.
- Consequences: No manual working/finalizing mode, project enforcement file, receipt freshness, session binding, or generic blocked prose is exposed.
- Validation: Focused policy tests and turn-finalization regressions pass before publication; acceptance scenarios verify concise “not yet complete” diagnostics.
- Reopen if: Real completion wording produces material false allows or false blocks that cannot be corrected without an explicit internal completion-intent signal.

### D-004 — Mark `hermes 1` with a hidden launch-context flag

- Level: Realization
- Question: How should the fork know that an invocation is decision-enforced without user configuration?
- Criteria: One stable user command; no public non-secret environment variable; plain Hermes unaffected; fixed maintained-fork/profile target; clear failure.
- Alternatives: Require `.hermes/enforcement.json` or a public environment variable; use a hidden CLI launch-context flag passed by the tracked wrapper.
- Selection: `scripts/hermes-one` invokes the maintained fork with `--profile decision` and an internal hidden enforcement flag.
- Tradeoff: The tracked wrapper contains a machine-specific maintained-fork path and must be synchronized to the machine-local launcher after review.
- Evidence: `scripts/hermes-one`, hidden parser/main plumbing, and `tests/hermes_cli/test_hermes_one_contract.py` exercise invocation, forwarding, marker activation, and missing-fork repair output.
- Assumptions: The maintained checkout path remains the stable local fork location requested by the user.
- Consequences: Plain `hermes` remains the standard installation; enforced skill injection is launch-scoped and prompt-cache stable.
- Validation: Repository wrapper tests plus real `hermes 1 --version`, `hermes 1 tools list`, and plain `hermes --version` checks after installation.
- Reopen if: Hermes gains a cleaner upstream alias/profile launch-context mechanism with the same one-command behavior.

### D-005 — Migrate once without deleting legacy files

- Level: Realization and Evolution
- Question: How should existing strict-protocol projects transition?
- Criteria: Preserve user data; do not invent decisions; no permanent dual-write mode; carry scope, fidelity, unresolved items, and reopening conditions.
- Alternatives: Maintain strict and lean protocols indefinitely; provide a one-way converter that leaves legacy files untouched.
- Selection: Provide `migrate_to_decision_ledger.py` as a one-way conversion and require user review before any archival.
- Tradeoff: Migration output may need human refinement because legacy documents vary and structural conversion cannot infer missing rationale safely.
- Evidence: The migration implementation and fixture tests preserve mapped content, leave source files unchanged, and report legacy files.
- Assumptions: Existing projects can be migrated from the documented legacy map/record shapes without permanent compatibility logic.
- Consequences: New projects use only the ledger; old project files are never silently deleted or archived.
- Validation: `tests/skills/test_design_protocol_migration.py` covers successful conversion and refusal to overwrite an existing ledger.
- Reopen if: A real legacy project exposes an unhandled shape that would lose user-authored decision evidence.

### D-006 — Make independent review risk-proportionate

- Level: Governance
- Question: Must every ordinary enforced design completion obtain runtime-trusted independent review?
- Criteria: Better outcomes for consequential work; low default ceremony; no unsupported provenance claims; user control.
- Alternatives: Require trusted reviewer snapshots and process-bound receipts for every completion; use independent review when risk, expense, publicity, irreversibility, safety, or explicit request warrants it.
- Selection: Remove mandatory review orchestration from the plugin and retain independent review as an ordinary risk-based agent action.
- Tradeoff: Ordinary completion carries no cryptographic or process-local claim of reviewer independence.
- Evidence: The plugin no longer registers `design_review_request`, legacy reviewer/receipt/snapshot modules are removed, and this substantial implementation still receives separate philosophy and maintainability reviews before publication.
- Assumptions: Review quality matters more than universal reviewer provenance for the default product.
- Consequences: Review findings must still be remediated for this high-impact fork correction, but no user-facing review stage becomes part of ordinary use.
- Validation: Fresh delegated reviews inspect the final diff and focused evidence; blocking findings trigger remediation and re-review.
- Reopen if: The product promise changes to require independent certification rather than decision discipline.

### D-007 — Limit the product claim to observable evidence

- Level: Language and Governance
- Question: What may the fork honestly claim after simplification?
- Criteria: Match actual implementation; avoid implying hidden cognition or universal security; remain useful and testable.
- Alternatives: Claim proof of comprehensive private reasoning and tamper-proof release; claim only skill loading, observable ledger discipline, and completion blocking on the local `hermes 1` path.
- Selection: Use the narrow reduced trust claim and fidelity-qualified completion language.
- Tradeoff: The claim is less ambitious but materially more defensible and understandable.
- Evidence: `NORTH_STAR.md`, `docs/design-enforcement.md`, the bundled skill, policy diagnostics, and tests state and enforce the boundary.
- Assumptions: Users prefer a reliable narrow guarantee over a complex broader claim.
- Consequences: Documentation must explicitly deny proof of private cognition, objective quality, evidence truth, reviewer intelligence, production readiness beyond fidelity, and universal tamper-proof delivery.
- Validation: Philosophy-fidelity review checks claim-to-code alignment and documentation consistency before publication.
- Reopen if: New technical evidence and explicit user approval support a revised, precisely scoped guarantee.

## Unresolved consequential decisions

- None

## Completion status

- Fidelity: Production implementation
- Supported claim: Production-implementation complete for the maintained fork's local `hermes 1` decision-enforcement path.
- Known limitations: The structural validator does not judge semantic design quality or evidence truth; completion/applicability detection remains heuristic; universal gateway, cron, ACP, proxy, media, subagent, and tamper-resistant release enforcement are outside scope; publication and installed-copy verification remain pending until the final gates run.
