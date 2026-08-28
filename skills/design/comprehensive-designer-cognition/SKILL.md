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

## Mandatory Design Completion Contract

The protocol has two modes:

- **Working mode** applies to exploration, a bounded critique, a small decision, or advice that does not claim a finished design. Keep reasoning proportionate, but label unresolved decisions and do not imply completion.
- **Completion mode** is mandatory when producing or materially revising a design artifact, implementing a design, specifying a reusable system, working across three or more decision levels, or making any completion claim. In a repository or writable project, completion mode requires the files and validator below.

The user may reduce scope or fidelity and may establish that a condition-dependent gate is genuinely not applicable. The non-waivable gates remain mandatory for every completion claim. Do not silently waive a gate. When evidence cannot be produced, report the work as provisional or blocked rather than complete.

### Gate A — Decision boundary

Before implementation or high-fidelity production, state:

- the design object;
- decision levels in scope;
- included surfaces, scenarios, actors, states, and repeated families;
- intentional exclusions;
- target fidelity;
- a qualified definition of done for this commitment.

Completion condition: the boundary prevents a polished subset from masquerading as the whole design.

### Gate B — Progressive decision expansion

For every committed parent decision, identify generated children. Expand children that are consequential, repeated, risky, uncertain, highly coupled, difficult to reverse, or likely to require a reusable rule. Continue until another capable designer could execute the in-scope branch without inventing governing logic.

Do not jump from an adjective or broad direction directly to a polished artifact. Expand the intervening decisions about objective, content, structure, behavior, variation, context, exceptions, failure, and realization as applicable.

Completion condition: every in-scope terminal commitment is either specified, validated, explicitly provisional, or recorded as a blocker.

### Gate C — Consequential decision records

Record every high-impact decision and every rule governing a repeated family. Each record must contain the question, criteria, at least two meaningful alternatives when alternatives exist, selection, tradeoffs, evidence versus assumptions, downstream consequences, validation method, and reopening condition.

Completion condition: high-impact choices can be challenged and traced without reconstructing hidden reasoning.

### Gate D — Repeated-system specification

For every repeated family—components, interactions, messages, roles, service moments, spatial modules, images, controls, rules, recommendations, or other recurring elements—define the applicable construction grammar:

- shared anatomy, behavior, or sequence;
- dimensions, boundaries, tolerances, alignment, and spacing;
- semantic roles and hierarchy;
- allowed variation and prohibited treatments;
- contextual or responsive transformation;
- accessibility and inclusion behavior;
- empty, loading, degraded, error, adversarial, and recovery behavior;
- maintenance and extension rules.

Mark non-applicable dimensions explicitly with a reason. A set of attractive or successful examples is not by itself a system.

Completion condition: a new instance can be created without relying on undocumented taste.

### Gate E — Novel-extension test

Create at least one additional in-scope example, scenario, or instance using only the documented system rules. Record every point where improvisation was required. Any consequential improvisation means the system is under-specified and must be revised or remain provisional.

Completion condition: the extension introduces no new governing rule, or each newly discovered rule has been incorporated and retested.

### Gate F — Artifact and perceptual audit

Inspect the actual artifact, not only its source or rationale. Select diagnostics appropriate to the medium. Examples include bounding boxes, baselines, optical centers, grayscale, silhouettes, small-size output, final context, physical tolerances, service walkthroughs, state traces, timing, stress conditions, and degraded operation.

For repeated perceptual elements, compare visual or experiential weight, hierarchy, alignment, rhythm, and semantic consistency across siblings.

Completion condition: `DESIGN-AUDIT.md` links each applicable diagnostic to evidence and findings.

### Gate G — Context and transformation audit

Test every major surface or experience under applicable changes in viewport, device, environment, input method, actor capability, data volume, localization, operating condition, and time. For responsive visual work, inspect hierarchy, crop, focal point, information preservation, collisions, line breaks, touch targets, reading order, component transformation, and movement between overlay and document flow.

Completion condition: adaptation is art-directed or system-directed, not inferred from absence of overflow or catastrophic failure.

### Gate H — Bottom-up critique

Before completion, ask:

- Which details contradict upstream intent or system rules?
- Which siblings carry inconsistent weight or behavior?
- Which repeated roles are treated differently without reason?
- Which dimensions, timings, thresholds, or colors are arbitrary?
- Which elements cannot be reproduced from documented rules?
- Which polished details conceal unresolved decisions?
- Which observed failures implicate an upstream decision?

Completion condition: each finding is resolved, accepted as an explicit tradeoff, moved out of scope, or recorded as a blocker.

### Gate I — Evidence-based completion language

Never use **complete** without a qualifier. Allowed claims are:

- **Concept complete** — intent, frame, and strategy are resolved for the stated scope.
- **System specified** — reusable rules, variations, and states are documented for the stated scope.
- **High-fidelity artifact complete** — the realized experience is finished and tested for the stated scope.
- **Production implementation complete** — the real target, data, integrations, accessibility, safety, security, and operational paths work for the stated scope.

Use **provisional**, **partially specified**, **validation pending**, **blocked**, or **ready for the next commitment** when the corresponding gate has not passed.

### Gate J — Independent completion review

The building agent must not certify its own substantial design as complete and must not author or alter the reviewer’s report or receipt. Before a completion claim:

1. Capture the original request verbatim in `ORIGINAL-REQUEST.md` and reconcile the declared boundary against every requested deliverable. A scope reduction requires user evidence; unilateral narrowing is not approval.
2. Finish all builder-owned artifacts and gates except independent review. Run deterministic validation far enough to resolve all pre-review structural errors.
3. Compute the review subject hash with `validate_design_completion.py --subject-hash <project-root>`.
4. Use `delegate_task` to create a genuinely separate reviewer session. Give it the original request, boundary, decision artifacts, system specification, actual artifact or implementation, diagnostics, and validation output. Use `templates/INDEPENDENT-REVIEW-PROMPT.md` as its role contract.
5. The reviewer—not the builder—must inspect the evidence, write `INDEPENDENT-REVIEW.md`, and create `REVIEW-RECEIPT.json` using `create_review_receipt.py` with its real child session identifier.
6. Resolve every blocking finding and obtain a fresh **pass**. A conditional pass is not a pass. Any material change to the request, manifest subject fields, or required artifacts invalidates the subject hash and receipt.

The receipt binds the review to exact artifact hashes and detects stale review, but it does not cryptographically prove reviewer independence. If a separate reviewer or runtime provenance is unavailable, do not self-certify. Report `awaiting independent review`.

### Gate K — Deterministic completion manifest

For substantial work in a writable project, initialize the protocol before implementation or high-fidelity production:

```text
python "${HERMES_SKILL_DIR}/scripts/init_design_protocol.py" <project-root>
```

This creates the builder-owned artifacts and a root `.hermes.md` without overwriting existing files. It deliberately does not create the reviewer-owned report or receipt. Capture the original request before interpreting its boundary, then maintain `DESIGN-COMPLETION.json` from `templates/DESIGN-COMPLETION.json`.

Every applicable gate must be `pass` with **structured evidence references**. Each evidence item must resolve uniquely to an existing textual project file and use exactly one locator: a unique structural Markdown section heading, a structured evidence ID matching `PREFIX-###`, or a strict RFC 6901 JSON Pointer for JSON evidence. Markdown parsing ignores fenced examples and consistently supports CommonMark ATX headings, including optional closing hashes. Evidence IDs must resolve exactly once as a Markdown anchor, table row, list item, HTML ID, or delimited token—not an arbitrary substring or prefix of a longer identifier. All JSON inputs reject duplicate object members, non-standard or non-finite numeric values, lone Unicode surrogates, excessive nesting, and ambiguous pointers. Binary evidence must be attached through a textual evidence index that records and matches its SHA-256 digest; a binary file cannot validate its own invented section or ID. The decision-boundary, progressive-expansion, consequential-records, artifact-audit, bottom-up-critique, automated-validation, and independent-review gates are non-waivable. Repeated-system and novel-extension gates may be `not_applicable` only when the manifest declares no repeated families; context-transformation may be `not_applicable` only when the manifest declares no transformations. Every exemption requires a concrete reason.

The validator also requires canonically distinct artifact files, exactly one structural occurrence of every mandatory artifact section outside fenced code, unique decision-node and record identifiers, exactly one node ID and at most one terminal record reference per map line, a status and valid record link for every committed or validated node, complete and non-duplicated decision-record fields outside fenced examples, an original-request hash, a separate reviewer-produced report whose structural subject, session, disposition, blocker section, and headings match its freshness receipt, and a receipt bound to every required artifact plus every textual evidence file and binary attachment cited by any pre-review gate. `fail`, `not_run`, `provisional`, missing evidence, stale review, unresolved blockers, or absent artifacts prohibit completion.

Run the completion gate:

```text
python "${HERMES_SKILL_DIR}/scripts/validate_design_completion.py" <project-root>
```

Treat a nonzero exit as a hard completion blocker. Do not edit the manifest merely to satisfy the validator; its values must point to real evidence.

### Anti-self-certification rule

Source files existing, an artifact rendering, tests passing, no visible overflow, general aesthetic coherence, or the builder's own approval are insufficient. A completion claim requires all applicable gates, required artifacts, deterministic validation, direct artifact inspection, extension tests for repeated systems, independent review, and zero unresolved blockers.

## Required Working Artifacts

For completion-mode work in a writable project, create and maintain all of these builder-owned files:

- `ORIGINAL-REQUEST.md`
- `DESIGN-BRIEF.md`
- `DECISION-MAP.md`
- `DECISION-RECORDS.md`
- `SYSTEM-SPEC.md`
- `DESIGN-AUDIT.md`
- `VALIDATION-REPORT.md`
- `DESIGN-COMPLETION.json`

A separate delegated reviewer owns:

- `INDEPENDENT-REVIEW.md`
- `REVIEW-RECEIPT.json`

The builder must not modify reviewer-owned files. Start from the files under `templates/`. These artifacts are part of the design, not retrospective paperwork. Update builder-owned artifacts as decisions change; any material change after review requires a new review. For working-mode conversation without a project, present the corresponding information inline and never claim completion.

### Design Brief

- Situation
- Intended effect
- People and systems affected
- Scope and non-goals
- Constraints
- Success and failure criteria
- Known evidence
- Explicit assumptions
- Open questions

### Decision Map

Represent live decisions as an indented tree or compact graph under one structural `## Decision tree` section; do not place the live tree in a fenced example. Mark dependencies, status, consequence, reversibility, and uncertainty. Expand only the active frontier.

### Decision Record

For completion-mode project files, use this validator-compatible structure exactly; duplicate it for each `DR-###` record:

```markdown
## DR-001 — Decision name

- **Level:**
- **Status:** open | provisional | committed | validated | reopened | blocked | out-of-scope
- **Question:**
- **Affected people or systems:**
- **Criteria:**
- **Alternative A:**
- **Alternative B:**
- **Selection:**
- **Tradeoffs and failure modes:**
- **Evidence:**
- **Assumptions:**
- **Downstream consequences:**
- **Consequence if wrong:**
- **Reversibility:**
- **Uncertainty:**
- **Validation method and result:**
- **Reopen if:**
```

### Coherence Check

- Does the whole express one intelligible governing logic?
- Can each major feature be traced to an intended effect?
- Do any local optimizations undermine the system?
- Are similar situations handled similarly unless difference is intentional?
- Does the perceptible form tell the truth about behavior and structure?
- Are omissions and exclusions deliberate?

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

In working mode, a result is **ready for the next commitment** when it has clear rationale, proportionate evidence, and no known contradiction hidden by presentation quality. In completion mode, use a qualified completion claim only after every applicable mandatory gate passes, the deterministic validator exits successfully, and an independent reviewer returns a fresh pass with zero blockers.