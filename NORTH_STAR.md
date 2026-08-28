# Decision-Enforcement North Star

## Why this fork exists

This fork exists for one reason:

> Make Hermes reliably apply the `comprehensive-designer-cognition` philosophy to substantial design work without forcing the user to understand or operate backend enforcement machinery.

The philosophy treats design as a hierarchy of interdependent decisions rather than a sequence of aesthetic choices or artifact-production tasks. Good design follows from exposing the right decisions, ordering them by consequence and dependency, comparing meaningful alternatives, naming tradeoffs, propagating consequences, validating proportionately, and reopening upstream decisions when reality disagrees.

The fork is not intended to become a general-purpose provenance, cryptographic review, workflow-management, or universal response-security product.

## Product promise

The target user experience is:

```bash
cd /path/to/project
hermes 1
```

The user then describes the design task normally. Hermes applies the decision philosophy automatically. When the user says an ordinary equivalent of “Finish this project,” Hermes either:

- releases a fidelity-qualified completion statement supported by the recorded decisions; or
- explains which consequential decisions remain unresolved and continues working.

The user should not need to know about policy IDs, modes, manifests, hashes, receipts, reviewer sessions, immutable snapshots, audit logs, or process-local state.

## Single enforceable rule

This is the governing invariant for the corrected fork:

> Before Hermes may claim a substantial design is finished, every consequential in-scope decision must be traceable from intent to implementation and must record its alternatives, selected direction, tradeoff, evidence or assumption, downstream consequence, validation status, and reopening condition; unresolved consequential decisions must be disclosed as unresolved rather than silently treated as complete.

Every retained backend mechanism must trace directly to this invariant. If a mechanism does not help enforce this rule, enable the decision philosophy, or provide the one-command user experience, it should be removed or made optional.

## The design philosophy being enforced

### Design is a decision system

A design is not a pile of outputs. It is a directed system of decisions:

- parent decisions constrain child decisions;
- sibling decisions must remain coherent;
- cross-cutting decisions affect multiple branches;
- local details can expose upstream contradictions;
- evidence can reopen prior decisions.

### Default hierarchy

Use this hierarchy as a flexible map:

1. **Situation** — what is happening now and why intervention is considered.
2. **Intent** — what effect should occur, for whom, and under what conditions.
3. **Frame** — what problem and system boundary are actually being designed.
4. **Strategy** — what mechanism or theory of change will produce the intended effect.
5. **System** — actors, components, relationships, flows, rules, authority, and states.
6. **Experience and behavior** — what people perceive, understand, decide, do, and recover from.
7. **Form and language** — perceptible expression that truthfully supports the strategy and behavior.
8. **Detail** — exact dimensions, words, timings, thresholds, transitions, and specifications.
9. **Realization and evolution** — implementation, governance, maintenance, learning, adaptation, and retirement.

The names may be adapted to the domain. The ordering principle remains: consequential upstream decisions precede dependent details.

### Required qualities of a consequential decision

A consequential decision should expose:

- the decision question;
- hierarchy level and dependencies;
- intended effect and affected people or systems;
- evaluation criteria;
- at least two meaningful alternatives when alternatives exist;
- selected direction;
- tradeoffs and failure modes;
- known evidence;
- explicit assumptions;
- downstream consequences;
- confidence or uncertainty;
- validation method and result;
- reopening condition.

Depth must remain proportionate. The system should not create performative paperwork for trivial, reversible choices.

### Governing principles

1. Purpose before expression.
2. Outcomes before features.
3. Structure before detail.
4. Relationships before components.
5. Constraints are generative.
6. Alternatives make decisions visible.
7. Tradeoffs must be named.
8. Coherence beats isolated excellence.
9. Evidence should match consequence.
10. Resolution should match certainty.
11. Design includes operation and change over time.
12. The designer is not the user.
13. Every solution changes the problem.
14. Omission is a decision.
15. Stop deliberately at the fidelity required for the current commitment.

## What must remain observable

The corrected implementation should maintain one project-level `DESIGN-DECISIONS.md` ledger for substantial writable-project work. It should contain:

- the design boundary and target fidelity;
- the live decision map;
- records for consequential decisions;
- unresolved consequential decisions;
- the supported completion claim and known limitations.

Supporting artifacts—briefs, specifications, prototypes, screenshots, tests, audits, research, or independent reviews—should be produced when appropriate to the design and risk. They are not universal backend ceremony.

## Completion language

Hermes must qualify completion according to what is actually supported. Examples include:

- **Concept complete** — intent, frame, and strategy are resolved for the stated scope.
- **System specified** — reusable rules, variations, and states are documented for the stated scope.
- **High-fidelity artifact complete** — the realized artifact is finished and tested for the stated scope.
- **Production implementation complete** — real integrations, accessibility, safety, security, and operational paths work for the stated scope.

When the evidence does not support completion, use language such as:

- provisional;
- partially specified;
- validation pending;
- blocked;
- ready for the next commitment.

## What the fork may honestly enforce

The corrected fork may claim:

> For substantial design work launched with `hermes 1`, Hermes loads the comprehensive decision philosophy, records consequential decisions in an observable ledger, and blocks its own completion claim when the ledger lacks required decision evidence.

## What the fork must not claim

The fork does not prove:

- private model cognition or hidden chain of thought;
- objective design quality;
- factual truth of evidence;
- reviewer intelligence or independence;
- production readiness beyond the stated fidelity;
- tamper-proof response delivery across every Hermes surface;
- that every decision is permanently correct.

The observable ledger and completion check enforce disciplined external behavior, not private cognition or universal truth.

## Scope boundaries

### In scope

- `hermes 1` as the single enforced-design entry point;
- automatic loading of the comprehensive decision skill;
- automatic creation and maintenance of one decision ledger;
- a narrow completion-claim check;
- actionable explanations when consequential decisions remain unresolved;
- fidelity-qualified completion language;
- optional validation and independent review proportional to risk;
- one maintained fork state and one migration path from the legacy protocol.

### Out of scope by default

- manual working/finalizing modes;
- per-project policy configuration;
- process-local signing receipts;
- mandatory reviewer agents;
- immutable review snapshots;
- parent-session binding;
- mandatory ten-file completion packages;
- exact candidate/released response hashing for design work;
- cross-surface gateway, cron, ACP, proxy, media, and Codex restrictions solely for design enforcement;
- user-operated reconciliation stages;
- permanent compatibility with two competing design protocols.

High-risk users may request stronger provenance separately, but it must not complicate the default product.

## Change test

Before adding or retaining functionality, answer:

1. Which part of the single enforceable rule does this support?
2. Is this needed for the `hermes 1` user experience?
3. Can the same outcome be achieved through the skill or one decision ledger?
4. Does this introduce a user-visible stage, mode, file, command, or recovery procedure?
5. Does its guarantee exceed the product promise and create backend drift?
6. Is the complexity proportional to the design risk it addresses?

If the functionality cannot be traced to the invariant or the one-command experience, remove it or make it optional.

## Success criteria

The correction is successful when:

- the user starts with `hermes 1` and no other setup command;
- the user works in ordinary design language;
- there are zero user-managed backend stages;
- one decision ledger is the only universal project artifact;
- unsupported completion claims are blocked with actionable decision-specific feedback;
- supported completion claims are fidelity-qualified;
- restarts do not invalidate ordinary decision evidence;
- plain `hermes` remains unaffected;
- the fork contains materially fewer changes than the current 65-file, roughly 6,949-line strict-provenance implementation;
- an independent reviewer confirms that retained code enforces decision discipline rather than paperwork.

## Authority and precedence

For this fork’s decision-enforcement work, use this precedence:

1. This North Star.
2. `docs/decision-enforcement/PRODUCT-DECISIONS.md`.
3. `docs/decision-enforcement/CORRECTION-PLAN.md`.
4. `docs/decision-enforcement/CURRENT-STATE.md`.
5. The bundled `comprehensive-designer-cognition` skill.
6. Existing strict-enforcement implementation and historical documentation.

When existing code or documentation conflicts with this North Star, treat the conflict as correction work—not as a reason to preserve the old behavior.
