# Enforced design decisions

1. `cd` into the project.
2. Run `hermes 1`.
3. Describe the design task normally.
4. Say “Finish this project” when ready.

Hermes records consequential decisions in `DESIGN-DECISIONS.md` and will not
claim completion while consequential decisions remain unresolved or
untraceable. There is no initialization command or user-managed lifecycle.

## Developer notes

The repository launcher source is `scripts/hermes-one`. It invokes the
maintained fork with the `decision` profile and a hidden launch-context flag.
The bundled policy injects the comprehensive design-decision skill only for
that launch context. It creates the ledger only when absent and invokes the
structural validator only when an assistant response attempts a design
completion claim.

The guarantee is deliberately limited: Hermes loads the decision philosophy,
records observable decision evidence, and gates its own completion claim. It
does not prove private cognition, objective design quality, evidence truth,
reviewer independence, production readiness, or tamper-proof delivery across
every Hermes surface.
