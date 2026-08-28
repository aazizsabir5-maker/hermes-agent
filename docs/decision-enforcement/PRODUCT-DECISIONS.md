# Product Decision Record

Statuses: `committed`, `implemented`, `reopened`, or `retired`. Every decision may be reopened only through an explicit user/product change with corresponding North Star, test, and claim-boundary updates.

## P-001 — Optimize for decision discipline, not provenance infrastructure

- **Status:** implemented
- **Selection:** Enforce observable comprehensive hierarchical design decisions.
- **Retired default:** Universal process-local reviewer provenance and exact response-release security.
- **Tradeoff:** The product makes a narrower, more defensible guarantee.
- **Reopen if:** The user requests a separate high-assurance provenance product and accepts its operational complexity.

## P-002 — Use one user entry point

- **Status:** implemented
- **Selection:** `hermes 1` from the project directory.
- **Retired default:** User-managed fork path, profile flag, plugin setting, or project initializer.
- **Reopen if:** Upstream gains a simpler alias/profile mechanism preserving the same one-command behavior.

## P-003 — Use zero user-managed backend stages

- **Status:** implemented
- **Selection:** Hermes performs internal checks automatically on attempted completion.
- **Retired default:** Working/finalizing modes, trusted-tool choreography, session preservation, receipt freshness, and reconciliation.
- **Reopen if:** A genuinely necessary user decision cannot be safely defaulted; expose only that decision, not backend stages.

## P-004 — Use one universal project artifact

- **Status:** implemented
- **Selection:** One `DESIGN-DECISIONS.md` ledger.
- **Retired default:** Eight builder documents plus reviewer report and receipt.
- **Tradeoff:** Rich briefs, specifications, screenshots, tests, and audits are proportionate supporting evidence, not universal files.
- **Reopen if:** Real use shows a consequential property cannot be represented or referenced clearly from one ledger.

## P-005 — Keep independent review proportional

- **Status:** implemented
- **Selection:** Review is optional or risk-triggered for ordinary work, and required by project process for this high-impact fork correction.
- **Use review when:** Work is high-risk, expensive, public, difficult to reverse, safety-relevant, or explicitly requested.
- **Tradeoff:** Ordinary completion carries no cryptographic reviewer-provenance claim.
- **Reopen if:** The product promise changes to require independent certification.

## P-006 — Gate completion claims, not ordinary exploration

- **Status:** implemented
- **Selection:** The runtime checks candidate substantial-design completion claims; exploratory and provisional responses remain usable.
- **Retired default:** Buffering/restricting every applicable design turn and unrelated delivery surface.
- **Tradeoff:** Completion/applicability detection is heuristic and the product does not claim universal anti-bypass delivery.
- **Reopen if:** Material false allows/blocks require a better internal completion-intent signal.

## P-007 — Require fidelity-qualified completion

- **Status:** implemented
- **Selection:** Every completion claim names supported scope and fidelity.
- **Examples:** Concept complete, system specified, high-fidelity artifact complete, or production implementation complete for a stated scope.
- **Reopen if:** Revised language and evidence still prevent unsupported scope/fidelity claims and the user approves the change.

## P-008 — Do not claim private cognition or objective truth

- **Status:** implemented
- **Selection:** Claim observable decision records, skill loading, and completion discipline only.
- **Non-claims:** Private reasoning, objective design quality, evidence truth, reviewer intelligence, universal tamper-proof delivery, or readiness beyond stated fidelity.
- **Reopen if:** New technical evidence supports a narrower revised claim and the user explicitly approves it.

## P-009 — Provide one-way migration, not permanent dual modes

- **Status:** implemented
- **Selection:** A tested converter creates the ledger without overwriting it, inventing decisions, or deleting legacy files.
- **Retired default:** Permanent strict/lean compatibility and dual-write.
- **Reopen if:** A real legacy shape cannot migrate safely without a time-bounded compatibility window.

## P-010 — Every retained backend hunk needs a North-Star justification

- **Status:** implemented
- **Selection:** Retained production changes must support mandatory skill injection, ledger validation, generic local completion support, or the `hermes 1` experience.
- **Evidence:** The final complexity report compares production paths and line counts with current upstream.
- **Reopen if:** A different complexity-control mechanism remains equally traceable and testable.

## P-011 — Preserve a self-contained maintained fork

- **Status:** implemented
- **Selection:** Track the North Star, product decisions, current state, correction plan, decision ledger, and fresh-session handoff in the repository.
- **Reason:** A new session must continue safely without relying on prior chat history.
- **Reopen if:** Equivalent authoritative repository-local context replaces these files without reducing continuity.
