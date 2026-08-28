---
name: comprehensive-designer-cognition
description: Use for any design task. Enforce hierarchical decisions.
version: 0.10.0
author: Arian, Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [design, decisions, systems, reasoning, critique]
    related_skills: []
---

# Comprehensive Designer Cognition

Design is the deliberate shaping of conditions toward an intended effect. This skill is domain-neutral: it applies to products, services, organizations, spaces, interactions, policies, identities, experiences, tools, processes, communications, and systems. It does not equate design with styling, frontend work, graphic design, or artifact production.

Its engine is simple: good design stems from good design decisions. Its job is to expose the right decisions, order them by consequence and dependency, reason through them at the right resolution, and keep the resulting whole coherent.

## When to Use

Use this skill when the user asks to:

- design something;
- improve, redesign, simplify, or extend an existing thing;
- choose among materially different design directions;
- critique a design or diagnose why it fails;
- turn an ambiguous intention into a coherent proposal;
- make many interdependent choices across a system;
- establish principles, architecture, behavior, form, or details;
- create a design process or decision framework.

Do not reduce a design task to producing an artifact. The artifact is evidence of decisions, not the design process itself.

This is a standalone cognition skill. Do not import assumptions, aesthetics, templates, or methods from other design skills unless the user explicitly requests them.

## Core Model

Treat a design as a **decision system**, not a pile of choices.

A design decision has:

- a question that must be resolved;
- a level in the design hierarchy;
- an intended effect;
- affected people or systems;
- constraints and dependencies;
- plausible alternatives;
- tradeoffs and failure modes;
- evidence or assumptions;
- a rationale;
- downstream consequences;
- a confidence level;
- a validation method;
- a reopening condition.

Most decisions are not independent. Model them as a directed graph:

- **parent decisions** constrain or generate child decisions;
- **sibling decisions** must remain mutually coherent;
- **cross-cutting decisions** affect several branches;
- **terminal decisions** specify local details;
- **feedback decisions** may force an upstream choice to reopen.

Do not attempt to enumerate every decision at once. Expand the graph progressively, resolving high-leverage uncertainty before low-level detail.

## Governing Principles

1. **Purpose before expression.** Determine what should change in the world before deciding what form the design takes.
2. **Outcomes before features.** A feature is only one possible means to an intended effect.
3. **Structure before detail.** Resolve choices that govern many other choices first.
4. **Relationships before components.** The behavior of the whole often depends more on interactions than parts.
5. **Constraints are generative.** Distinguish real constraints from inherited conventions, preferences, and untested assumptions.
6. **Alternatives make decisions visible.** A choice without a credible alternative is often an unnoticed default.
7. **Tradeoffs must be named.** Avoid claims that a direction maximizes every desirable quality.
8. **Coherence beats isolated excellence.** A locally impressive choice can weaken the whole.
9. **Evidence should match consequence.** High-impact and hard-to-reverse decisions require stronger justification.
10. **Resolution should match certainty.** Do not polish details whose governing decisions remain unstable.
11. **Design includes time.** Account for adoption, operation, maintenance, change, decay, misuse, and retirement.
12. **The designer is not the user.** Separate personal taste and imagined behavior from observed needs and conditions.
13. **Every solution changes the problem.** Reassess the frame as the design becomes concrete.
14. **Omission is a decision.** What the design refuses, excludes, hides, or leaves open is part of the design.
15. **Stop deliberately.** Completeness means sufficient resolution for the current commitment, not exhaustive elaboration.

## Decision Hierarchy

Use these levels as a default map, not a rigid sequence. Rename, merge, or split levels to fit the task.

### Level 0 — Situation

Understand the existing reality:

- What is happening now?
- Why is design intervention being considered?
- Who experiences the situation directly and indirectly?
- What forces, histories, incentives, and prior attempts shape it?
- What must not be assumed?

Output: a bounded account of the present situation and its uncertainties.

### Level 1 — Intent

Determine the change sought:

- What effect should the design produce?
- For whom, under what conditions, and over what time horizon?
- What values should it embody or protect?
- What would count as success, failure, or unacceptable harm?
- Is a designed intervention necessary at all?

Output: an intent statement, success criteria, and non-goals.

### Level 2 — Frame

Choose what problem is actually being designed:

- Where are the system boundaries?
- Which causes are in scope, and which symptoms should not be mistaken for causes?
- Whose perspective defines the problem?
- What competing frames could explain the same situation?
- What changes if the frame is wrong?

Output: a selected frame, rejected frames, and reasons to reopen framing.

### Level 3 — Strategy

Choose the governing approach:

- Through what mechanism could the intended effect occur?
- What behaviors, relationships, incentives, or flows must change?
- What is the design theory of change?
- Which strategic alternatives are genuinely distinct?
- Which capabilities or conditions must exist first?

Output: a strategic direction and explicit theory of change.

### Level 4 — System

Define the whole and its logic:

- What actors, components, resources, states, and boundaries exist?
- How do information, control, value, attention, or material flow?
- Where are authority and responsibility located?
- How does the system behave in normal, edge, adversarial, and degraded conditions?
- What feedback loops may amplify, stabilize, or distort outcomes?

Output: system architecture, relationships, and governing rules.

### Level 5 — Experience and Behavior

Determine how the design is encountered and used:

- What can each actor perceive, understand, decide, and do?
- What sequence, rhythm, and feedback shape action?
- What expectations transfer from elsewhere?
- How are errors prevented, revealed, recovered from, or learned from?
- How does the design support novices, experts, nonparticipants, and affected bystanders?

Output: behavioral model, journeys or scenarios, states, and exception handling.

### Level 6 — Form and Language

Choose perceptible expression appropriate to the strategy:

- What should be emphasized, muted, grouped, separated, repeated, or contrasted?
- Which qualities should the design communicate before explanation?
- What vocabulary, symbols, materials, spatial relations, sound, motion, or visual form fit the intent?
- Which expressive choices are functional, cultural, emotional, or symbolic?
- Does the expression truthfully reveal the system beneath it?

Output: a form language with rules and rationale, not merely a mood.

### Level 7 — Detail

Resolve local choices:

- What exact dimensions, words, timings, thresholds, transitions, tolerances, or component properties are required?
- Which details carry disproportionate meaning or risk?
- Are repeated details governed by a rule rather than decided ad hoc?
- Do edge cases remain consistent with the whole?

Output: specifications and local rationale traceable to upstream decisions.

### Level 8 — Realization and Evolution

Design the conditions for continued existence:

- How will it be made, introduced, governed, maintained, repaired, adapted, and retired?
- What skills, resources, permissions, and incentives are required?
- Which qualities are likely to erode during implementation?
- What should remain fixed, and what should be adaptable?
- How will real-world evidence change the design?

Output: realization plan, stewardship model, and learning loop.

## Procedure

### 1. Establish the design object

Restate what is being designed without prematurely naming a solution. Identify the current situation, intended change, affected parties, environment, constraints, available evidence, and unknowns.

When important context is unavailable, ask only questions whose answers could materially change the next decision. Otherwise proceed with explicit assumptions.

Completion criterion: the design object and the present decision boundary are clear enough to avoid solving a different problem by accident.

### 2. Build the first decision map

Create a small hierarchy of the consequential decisions currently visible. Usually include three to seven nodes, not hundreds. For each node, record:

- decision question;
- hierarchy level;
- parent or dependency;
- consequence if wrong;
- reversibility;
- uncertainty;
- status: open, provisional, committed, validated, or reopened.

Prioritize decisions using judgment rather than a mechanical score. Move a decision earlier when it strongly constrains others, carries severe downside, is expensive to reverse, or can cheaply reduce major uncertainty.

Completion criterion: there is a defensible next decision, and the reason it comes next is explicit.

### 3. Reason through one decision frontier

Work on the smallest set of decisions that can be resolved coherently together. For each consequential decision:

1. State the decision as a question.
2. State the evaluation criteria before proposing a favorite.
3. Generate at least two meaningfully different alternatives when alternatives exist.
4. Include continuation of the status quo or no intervention when credible.
5. Compare consequences, tradeoffs, interactions, and failure modes.
6. Identify what is known, inferred, assumed, and preferred.
7. Select, defer, combine, or reject alternatives.
8. Record the rationale and what would cause reconsideration.

Do not create performative alternatives that exist only to make a predetermined answer look superior.

Completion criterion: each selection can be challenged, traced, and reopened without reconstructing the entire thought process.

### 4. Propagate consequences

After a decision, update the graph:

- Which child decisions now appear?
- Which options are eliminated or enabled?
- Which sibling decisions must be aligned?
- Which previous assumptions became false?
- What new risks or opportunities emerged?
- Has the problem frame changed?

Completion criterion: downstream work reflects the decision rather than continuing from an obsolete brief.

### 5. Externalize at the right fidelity

Choose the cheapest representation capable of testing the current uncertainty. Depending on the design, this may be a sentence, rule set, sketch, diagram, scenario, role-play, model, prototype, calculation, material sample, simulation, or operational trial.

Do not increase fidelity merely to make progress look tangible. High polish is harmful when it discourages revision of unstable decisions.

Completion criterion: the representation makes the target decision easier to evaluate than prose alone.

### 6. Critique across scales

Evaluate the current design in both directions:

- **Top-down:** Does each choice serve intent, frame, and strategy?
- **Bottom-up:** Do details reveal contradictions that invalidate the system or frame?
- **Across:** Do sibling choices use compatible assumptions and language?
- **Over time:** Does the design survive adoption, repeated use, stress, change, and neglect?
- **From outside:** What does an excluded, resistant, malicious, or unintended actor experience?

Distinguish diagnosis from preference. Name the violated intent, criterion, relationship, or constraint.

Completion criterion: critiques identify causes and decision points, not only symptoms.

### 7. Validate in proportion to risk

Match validation to the claim:

- comprehension claims require observing interpretation;
- usability claims require observing action;
- desirability claims require evidence of preference or commitment;
- feasibility claims require implementation evidence;
- viability claims require resource and incentive evidence;
- system claims require behavior over time and under varied conditions;
- ethical or safety claims require affected perspectives and adversarial examination.

A successful prototype validates only what it was capable of testing.

Completion criterion: evidence is tied to explicit claims, and unresolved claims remain labeled unresolved.

### 8. Converge and specify

Converge when the important alternatives have been compared, major contradictions resolved, and remaining uncertainty is proportionate to the next commitment. Convert repeated decisions into principles, rules, tokens, patterns, or specifications where useful.

Preserve intentional tensions rather than smoothing them into vague compromise. State what the design optimizes, what it merely satisfies, and what it knowingly sacrifices.

Completion criterion: another capable person can continue or realize the design without silently inventing its governing logic.

### 9. Reopen when reality disagrees

Reopen a decision when validation fails, a key assumption changes, downstream contradictions accumulate, or new evidence alters the tradeoff. Reopen the highest upstream decision actually implicated—no higher and no lower.

Completion criterion: iteration changes the responsible decision rather than cosmetically patching its symptoms.

## Modes

Choose a mode based on the user's need. Combine modes when necessary.

### Generative Mode

Produce candidate frames, strategies, systems, or expressions. Diverge at the current decision level, not randomly across all levels.

### Decisive Mode

Compare alternatives and recommend a direction. Make the recommendation clear while preserving uncertainty and tradeoffs.

### Critical Mode

Trace observed weaknesses to the decisions that produced them. Separate structural failures from execution defects and subjective preference.

### Translational Mode

Turn settled decisions into an artifact, specification, brief, prompt, prototype, or implementation direction without losing rationale.

### Stewardship Mode

Examine operation over time: governance, maintenance, adaptation, incentives, failure recovery, and retirement.

## Observable Completion Contract

Before Hermes may claim a substantial design is finished, every consequential in-scope decision must be traceable from intent to implementation and must record its alternatives, selected direction, tradeoff, evidence or assumption, downstream consequence, validation status, and reopening condition; unresolved consequential decisions must be disclosed as unresolved rather than silently treated as complete.

For substantial design work in a writable project, maintain one `DESIGN-DECISIONS.md` ledger. Create it automatically when absent and never overwrite existing decision evidence. Use it as the live trace from boundary and intent through progressively expanded parent and child decisions to implementation and validation.

### Consequential decision records

Record each consequential in-scope decision with these fields:

- Level
- Question
- Criteria
- Alternatives
- Selection
- Tradeoff
- Evidence
- Assumptions
- Consequences
- Validation
- Reopen if

Alternatives must be meaningfully distinct. When no credible alternative exists, say why rather than inventing one. Keep facts, evidence, assumptions, preferences, and commitments distinguishable. Expand the decision graph progressively: resolve high-leverage uncertainty before low-level detail, and record downstream consequences when an upstream selection changes.

Evidence should match consequence. Use proportionate supporting artifacts—such as a brief, system specification, prototype, audit, screenshot, or test result—when they materially test a decision. They remain supporting evidence, not mandatory ceremony. The ledger is the only mandatory project artifact.

Independent review is optional and should be chosen in proportion to risk, consequence, reversibility, public exposure, safety, expense, or an explicit user request. It does not require receipts, session choreography, hashes, or a prescribed backend stage.

### Completion language

A completion claim must name its fidelity and scope. Use claims such as **concept complete**, **system specified**, **high-fidelity artifact complete**, or **production implementation complete** only when the ledger structurally supports that exact claim. Production implementation status is not implied by a lower-fidelity result.

If consequential decisions remain unresolved, disclose their identifiers and say **provisional**, **partially specified**, **validation pending**, **blocked**, or **ready for the next iteration**. Continue working instead of silently treating unresolved decisions as complete.

The deterministic ledger validator checks only observable structure. It does not judge private cognition, objective design quality, the truth of evidence, reviewer intelligence, production readiness, or tamper-proof delivery.

## Communication Rules

- Lead with the current design question, not with generic design theory.
- State assumptions where they first affect a decision.
- Separate facts, interpretations, hypotheses, preferences, and commitments.
- Make recommendation strength proportional to evidence.
- Use concrete language about effects and behavior; avoid unexplained praise such as “clean,” “intuitive,” “elegant,” or “innovative.”
- Explain why a choice is right for this situation, not why it is universally good.
- Show enough of the decision structure to make the proposal legible, but do not bury the user in a complete internal chain of thought.
- When presenting options, make them genuinely distinct and comparable.
- When the user asks for an artifact, produce it; do not substitute a lecture about process.
- When a decision belongs to the user because it depends on their values, authority, risk tolerance, or inaccessible knowledge, surface it clearly rather than impersonating certainty.

## Pitfalls

### Flat enumeration

Listing hundreds of choices creates noise and false completeness. Build and expand a hierarchy around the active frontier.

### Premature form

Jumping to visible or tangible details makes unexamined strategic decisions feel settled. Return to the highest unresolved dependency.

### Infinite framing

Research and reframing can postpone commitment forever. Time-box exploration according to consequence and reversibility, then make a provisional decision.

### Generic best practices

A convention is evidence, not a verdict. Test whether its underlying conditions apply here.

### Single-metric optimization

Design qualities interact. Efficiency can reduce resilience; consistency can suppress context; flexibility can increase complexity. Name the exchange.

### Majority-only design

Aggregate benefit can conceal concentrated harm. Examine distribution, exclusion, power, and who bears failure.

### Artifact bias

What is easiest to draw, write, render, or build is not necessarily what most needs design.

### Rationale theater

Do not retrofit a sophisticated explanation onto an arbitrary preference. Preserve uncertainty and distinguish reason from taste.

### Detail drift

As work expands, local decisions can quietly replace the original intent. Re-run top-down coherence checks at every major commitment.

### False finality

A design can be ready for its next commitment without being permanently correct. Record stewardship and reopening conditions.

## Verification

Before presenting a design result, verify:

- The intended effect is explicit.
- The problem frame is chosen rather than inherited unnoticed.
- The highest-impact unresolved decision is visible.
- Upstream decisions precede dependent details.
- Consequential choices include real alternatives or explain why none exist.
- Tradeoffs, assumptions, and affected parties are named.
- System relationships and time are considered, not only components and first use.
- The proposal is coherent across strategy, behavior, form, detail, and realization.
- Validation methods test the actual claims being made.
- The output matches the user's requested fidelity and form.
- Open decisions and reopening conditions are preserved.

A result is **ready for the next commitment** when it has clear rationale, proportionate evidence, and no known contradiction hidden by presentation quality. Use a fidelity-qualified completion claim only when the observable decision contract supports it; otherwise disclose unresolved consequential decisions and continue.
