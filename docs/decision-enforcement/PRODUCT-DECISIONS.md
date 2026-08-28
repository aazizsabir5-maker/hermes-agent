# Product Decision Record

These entries separate user-confirmed direction from recommended corrections that still require implementation approval. They are product decisions and proposals, not descriptions of the current strict implementation.

- **committed** — directly established by the user or required for an honest claim boundary;
- **proposed** — recommended by the review and correction plan but not authorization to implement;
- **implemented** — reserved for behavior merged and verified in the corrected fork.

No entry in this document authorizes code changes by itself. Follow the approval checkpoint in `CORRECTION-PLAN.md`.

## P-001 — Optimize for decision discipline, not provenance infrastructure

- **Status:** committed
- **Question:** What should the fork primarily enforce?
- **Selection:** Observable use of the comprehensive hierarchical design-decision philosophy.
- **Rejected default:** Universal process-local reviewer provenance and exact response-release security.
- **Reason:** The original need was better design decisions. The strict provenance system created user-visible stages and backend drift beyond that need.
- **Tradeoff:** The corrected fork will make a narrower security claim.
- **Reopen if:** The user explicitly requests a separate high-assurance provenance product and accepts its operational complexity.

## P-002 — Use one user entry point

- **Status:** committed
- **Question:** How should enforced design work start?
- **Selection:** `hermes 1` from the project directory.
- **Rejected default:** Remembering a fork path, profile flag, plugin setting, or project initializer.
- **Reason:** The enforcement system should disappear behind one stable command.
- **Reopen if:** Hermes gains a cleaner upstream profile/alias mechanism that preserves the same one-command experience.

## P-003 — Use zero user-managed backend stages

- **Status:** committed
- **Question:** Should users manage working, review, reconciliation, and finalizing stages?
- **Selection:** No. Hermes handles any internal checks automatically when the user asks to finish.
- **Rejected default:** Manual mode changes, trusted-tool choreography, session preservation, and manifest reconciliation.
- **Reason:** These stages teach the backend instead of supporting design work.
- **Tradeoff:** Internal completion-intent detection must be tested carefully.
- **Reopen if:** A genuinely necessary user decision cannot be inferred or safely defaulted; surface only that decision, not implementation stages.

## P-004 — Use one universal project artifact

- **Status:** proposed
- **Question:** What evidence should every substantial writable-project design maintain?
- **Selection:** One `DESIGN-DECISIONS.md` ledger.
- **Rejected default:** Eight builder documents plus reviewer report and receipt.
- **Reason:** One ledger can expose boundary, hierarchy, consequential decisions, unresolved items, validation, and supported completion language without universal paperwork.
- **Required trace:** Each consequential decision must connect the governing intent and selected direction to a concrete artifact or representation appropriate to the claimed fidelity. Local references must remain inside the project and exist; this checks observable trace structure, not semantic truth.
- **Tradeoff:** Rich briefs, specifications, screenshots, tests, and audits become proportional supporting evidence rather than universal files.
- **Reopen if:** Executable tests show that a required property cannot be represented or referenced clearly from one ledger.

## P-005 — Keep independent review proportional

- **Status:** proposed
- **Question:** Must every substantial design obtain a runtime-trusted independent review?
- **Selection:** No. Review is optional or risk-triggered.
- **Use review when:** Work is high-risk, expensive, public, difficult to reverse, safety-relevant, or explicitly requested.
- **Reason:** Independent review can improve outcomes, but process-local receipts and reviewer sessions do not directly enforce the design philosophy.
- **Tradeoff:** Ordinary completion will not carry a cryptographic reviewer-provenance claim.
- **Reopen if:** The user changes the product promise to require independent certification.

## P-006 — Gate completion claims, not ordinary exploration

- **Status:** proposed
- **Question:** When should runtime enforcement block output?
- **Selection:** Only when Hermes attempts to claim that substantial design work is finished.
- **Rejected default:** Buffering or restricting all applicable design turns and delivery surfaces.
- **Reason:** Exploration must remain fluid; the core risk is unsupported finality.
- **Tradeoff:** The system does not claim universal pre-release confidentiality or anti-bypass behavior.
- **Reopen if:** A separate security requirement is established with explicit scope and acceptance criteria.

## P-007 — Require fidelity-qualified completion

- **Status:** committed
- **Question:** What completion language may Hermes use?
- **Selection:** Scope- and fidelity-qualified claims only.
- **Examples:** Concept complete, system specified, high-fidelity artifact complete, or production implementation complete for a stated scope.
- **Reason:** “Complete” without fidelity silently overstates what was designed and validated.
- **Reopen if:** Never; wording may evolve, but the qualification principle remains.

## P-008 — Do not claim private cognition or objective truth

- **Status:** committed
- **Question:** What does enforcement prove?
- **Selection:** Observable decision records and completion discipline only.
- **Non-claims:** Private reasoning, objective quality, evidence truth, reviewer intelligence, and permanent correctness.
- **Reason:** Runtime procedures cannot establish those properties.
- **Reopen if:** Never without materially new technical evidence and an independently reviewed claim boundary.

## P-009 — Provide one-way migration, not permanent dual modes

- **Status:** proposed
- **Question:** How should existing strict-protocol projects transition?
- **Selection:** A tested one-way migration to `DESIGN-DECISIONS.md`.
- **Rejected default:** Maintaining strict and lean protocols indefinitely.
- **Reason:** Parallel systems recreate the drift and confusion being corrected.
- **Safety:** Do not delete or archive project files without user approval; migration must not invent decisions.
- **Reopen if:** A time-bounded compatibility window is technically necessary, with an explicit deletion date.

## P-010 — Every retained backend hunk needs a North-Star justification

- **Status:** proposed
- **Question:** How should implementation scope be controlled?
- **Selection:** Maintain a requirement-to-diff matrix during correction.
- **Rule:** Every retained production hunk must support the single invariant, mandatory skill injection, the one-ledger check, or the `hermes 1` experience.
- **Reason:** This prevents provenance machinery from surviving through inertia.
- **Reopen if:** Never; new requirements can be added, but they must be explicit and approved.
