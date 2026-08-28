# Fail-closed design completion enforcement

This fork adds a generic **required finalization policy** boundary to Hermes and
ships `design_enforcement` as its first strict policy.

## What is enforced

When a required finalization policy applies to the current conversation, Hermes buffers candidate
assistant text instead of streaming it. The complete response is transformed,
sanitized, evaluated, and durably audited before it is persisted or returned to
CLI, TUI, gateway, ACP, cron, or one-shot callers. A required policy must return
an explicit typed allow decision. Exceptions, malformed results, timeouts,
missing policies, invalid project policy files, audit-write failures, and deny
decisions all replace the candidate with a host-authored blocked response.

The bundled design policy:

- auto-loads as a bundled backend plugin;
- freezes the complete `comprehensive-designer-cognition` skill into the system
  prompt for applicable sessions at session creation;
- distinguishes deterministic working mode from final-delivery attempts;
- executes the bundled validator in a bounded subprocess;
- requires an independent reviewer created through Hermes' trusted subagent
  lifecycle;
- reviews a content-addressed, read-only snapshot containing only the manifest,
  declared artifacts, evidence indexes, and declared attachments, with file-read
  tools only; unrelated files such as `.env` are never copied;
- binds the review to parent session, reviewer session/model, canonical subject
  hash, report hash, and a process-trusted HMAC receipt;
- invalidates review after relevant subject or report changes;
- writes a durable host audit before releasing the response.

## Enable a project requirement

Create `.hermes/enforcement.json` in the project root (or copy
`docs/examples/design-enforcement.json`):

```json
{
  "schema_version": 1,
  "required_policies": ["design-completion"],
  "design": {
    "applicable": true,
    "mode": "working"
  }
}
```

The parser rejects duplicate members, non-finite values, duplicate or invalid
policy IDs, oversized files, and symlinked policy files. If a named required
policy is unavailable, the turn remains buffered and final delivery is blocked.

For the finalization turn, set `design.mode` to `"finalizing"`. This is the
strongest explicit runtime-owned signal. Even in working mode, deterministic
completion-claim detection triggers the final gate for applicable design work.

Do **not** launch an enforced project with `--safe-mode` or `--ignore-rules`.
The fork refuses these combinations at CLI startup.

## Workflow

1. Start Hermes in the project root using this fork.
2. Complete the builder-owned artifacts described by
   `skills/design/comprehensive-designer-cognition/SKILL.md`.
3. Run the bundled validator in working mode as often as needed:

   ```bash
   python skills/design/comprehensive-designer-cognition/scripts/validate_design_completion.py .
   ```

4. After builder-owned state is final, call the model-visible
   `design_review_request` tool. Core snapshots the project, launches a distinct
   reviewer child, validates its structured pass, and writes reviewer-owned
   `INDEPENDENT-REVIEW.md` and `REVIEW-RECEIPT.json` plus a trusted receipt under
   the active Hermes profile.
5. Set project mode to `"finalizing"` and make the fidelity-qualified completion
   claim. Core reruns the validator, verifies the trusted receipt, writes the
   finalization audit, and only then releases the response.

Remote gateway proxy execution and the opt-in Codex app-server runtime are
refused for applicable required-policy turns because those runtimes can emit or
persist model output outside the local finalization boundary. Use a locally
gated Hermes provider path for enforced completion turns.

When buffering is armed, ordinary output-transform and observability hooks receive
no candidate payload. Usage metadata may still be reported, but assistant prose,
provider reasoning fields, and tool-call names/arguments are withheld. Incremental
session writes store only redacted assistant rows until the release gate persists
the approved response. A host-level return backstop finalizes any inner-loop early
return that lacks finalization metadata.

To preserve the audited release hash, late delivery-surface media-path repair and
API data-URL rewriting are disabled for gated responses. Ensure any `MEDIA:`
references are canonical before the finalization turn.

## Trusted runtime state

Profile-aware host files are stored below the active `HERMES_HOME`:

- `enforcement/finalization-audit.jsonl`
- `enforcement/design-receipts/<parent-session>/...json`
- `enforcement/design-snapshots/<snapshot-sha256>/`

The receipt signing secret is process-local and is never placed in source,
environment variables, project files, or tool output. Restarting Hermes expires
trusted receipts by design and requires a fresh review.

## Security and provenance boundaries

The fork can enforce response buffering, callback outcomes, bounded subprocess
execution, exact file hashes, project-policy presence, durable audit ordering,
and Hermes-recorded parent/child lineage. It cannot mathematically prove that
evidence is truthful, that a model review is insightful, or that a design is
objectively good. Read-only snapshots are permission-hardened and reviewer tools
are restricted, but they are not a separate kernel/user/container trust domain;
a process with the same operating-system account can still alter local files.
Use a sandboxed execution backend when stronger filesystem isolation is needed.

Model prose and project-local review JSON are not accepted as reviewer
provenance. The host-issued receipt is mandatory in addition to the standalone
validator contract.
