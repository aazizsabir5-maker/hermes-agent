# Design completion rules

For every design task in this repository:

1. Load `comprehensive-designer-cognition` before making design decisions.
2. Capture the original request verbatim in `ORIGINAL-REQUEST.md`. Any scope reduction must be quoted from or approved by the user; the builder may not narrow scope unilaterally.
3. State the decision boundary, target fidelity, exclusions, and qualified definition of done before implementation or high-fidelity production.
4. Use completion mode for substantial design work; maintain all protocol artifacts and `DESIGN-COMPLETION.json`.
5. Expand every committed parent into consequential, repeated, risky, uncertain, coupled, and hard-to-reverse child decisions. Do not polish an unresolved branch.
6. Give live decision nodes stable `DM-###` identifiers under the structural `## Decision tree` section in `DECISION-MAP.md`; fenced DM examples are not live map evidence. Give consequential records stable `DR-###` identifiers.
7. Record every high-impact decision and every rule governing a repeated family.
8. Specify a reproducible grammar for every repeated family and run a novel-extension test using only documented rules.
9. Inspect the actual artifact under all applicable contexts, transformations, states, failures, and diagnostic views.
10. Every passing gate must cite structured evidence that resolves uniquely outside fenced-code examples to an existing textual file using exactly one locator: a unique structural Markdown section, a `PREFIX-###` exact evidence anchor, or a strict RFC 6901 JSON Pointer. CommonMark ATX closing hashes are supported consistently. Mandatory Markdown sections, decision records, and review declarations must likewise exist structurally outside fenced code; review subject/session declarations belong only in `Review scope`, disposition only in `Disposition`, and blockers only in `Blocking findings`. JSON inputs may not contain duplicate members, non-standard or non-finite numbers, lone Unicode surrogates, or excessive nesting. Binary evidence must be attached through a textual evidence index containing its verified SHA-256 digest. Core gates may not be marked not applicable.
11. Run a bottom-up sibling-coherence audit and resolve or explicitly block every finding.
12. The builder may not approve its own completion or create the reviewer-owned files. A separate delegated reviewer must create `INDEPENDENT-REVIEW.md` and `REVIEW-RECEIPT.json`; its declared subject hash and session must match the receipt.
13. Any material change to a required artifact, textual gate-evidence file, or binary attachment after review invalidates the receipt and requires a fresh independent review.
14. Run the final deterministic completion validator only after receipt creation. Keep its final stdout external; do not edit a subject artifact to paste it back in, because that would invalidate the receipt.
15. Do not use “complete” without one of the qualified fidelity claims defined by the skill.
16. Never change evidence or manifest status merely to satisfy the validator; every value must describe real work.

If an applicable gate cannot run, report the work as provisional, validation pending, blocked, or awaiting independent review—not complete.
