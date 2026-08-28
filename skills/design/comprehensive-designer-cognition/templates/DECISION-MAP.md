# Decision Map

Status vocabulary: `open`, `provisional`, `committed`, `validated`, `reopened`, `out-of-scope`, `blocked`.

Give every node one stable decision-map identifier and one status on the same tree line. Every committed or validated node must reference one decision record. Include consequence, reversibility, and uncertainty in that record.

## Decision tree

DM-001 Design object [status] (record: DR-001)
├── DM-010 Intent [status] (record: DR-010)
├── DM-020 Frame [status] (record: DR-020)
├── DM-030 Strategy [status] (record: DR-030)
├── DM-040 System [status] (record: DR-040)
│   └── DM-041 Repeated family [status] (record: DR-041)
│       ├── DM-042 Governing rule [status] (record: DR-042)
│       ├── DM-043 Allowed variation [status] (record: DR-043)
│       ├── DM-044 Exception and failure behavior [status] (record: DR-044)
│       └── DM-045 Novel extension [status] (record: DR-045)
├── DM-050 Experience and behavior [status] (record: DR-050)
├── DM-060 Form and language [status] (record: DR-060)
├── DM-070 Detail [status] (record: DR-070)
└── DM-080 Realization and evolution [status] (record: DR-080)

Delete out-of-scope example branches rather than leaving irrelevant sample nodes. Open and provisional nodes may omit a record only when no consequential choice has yet been made.

## Active frontier

[Smallest coherent set of decisions currently being resolved.]

## Cross-cutting decisions

[Decisions that constrain several branches.]

## Unresolved in-scope nodes

[List every open, provisional, reopened, or blocked node. Explain whether it blocks the current qualified definition of done.]

## Expansion audit

For every committed parent:

- What children did it generate?
- Which are consequential, repeated, risky, uncertain, coupled, or hard to reverse?
- Which need rules rather than one-off judgment?
- Can another capable designer execute every terminal in-scope branch without inventing governing logic?
